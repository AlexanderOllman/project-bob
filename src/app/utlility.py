from langchain.prompts import (
    HumanMessagePromptTemplate, MessagesPlaceholder
)
from langchain_core.globals import set_verbose
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.postprocessor.nvidia_rerank import NVIDIARerank
from src.app.api.databaseUtil import MetaTableFetch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, format_document, SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from llama_index.core import VectorStoreIndex
from src.app.api.databaseUtil import VectorStoreBasedOnTable
from langchain.globals import set_debug
from llama_index.core import Settings
from operator import itemgetter
from langchain.prompts.prompt import PromptTemplate
from langchain_community.retrievers import LlamaIndexRetriever

from src.app.llm import get_llm, get_embedding, get_foundation_model_used_for_embedding, get_embed_dim, MISTRAL, NIM_KEY, CONTRACT

set_debug(True)
set_verbose(False)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

# constants
eventInterpretation = "EI"
QuestionSummaryStr = "questionSummary"
GenericQuestions = "generic"
Ezmeral = "ezmeral"
Greenlake = "greenlake"
StandAloneQuestion = "standalonequestion"

import logging
import os
import sys
import time


llm = get_llm()


system_template = """You are an legal assistant for question-answering tasks who takes the persona of a paralegal. Use context to answer the question. 
Dont make up things, only answer from the Context. Be specific. Be as accurate as possible with the context and dont look for synonyms.
Question: {question} Chat history: {history} Context: {context} Answer:"""

human_template = """
Question: {question} 
"""

stand_alone_question_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
    Chat History:
    {history}
    Follow Up Input: {question}
    Standalone question:"""

messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template),
]

prompt_template = PromptTemplate.from_template(
    "Tell me a {adjective} joke about {content}."
)

qa_prompt = ChatPromptTemplate.from_messages(messages)
# qa_prompt = prompt_template.from_template(system_template)

def combineDocuments(
        docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def  sentenceWindowPostProcessorAndReranker(index, similarity_top_k=7, rerank_top_n=3):
    logging.info("sentenceWindowTransformerAndReranker function")

    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")

    rerank = NVIDIARerank(model="nv-rerank-qa-mistral-4b:1",top_n=rerank_top_n,api_key=os.getenv(NIM_KEY))

    engine = index.as_query_engine(
        chat_mode=ChatMode.SIMPLE,
        similarity_top_k=similarity_top_k,
        node_postprocessors=[postproc,rerank]
    )

    return engine


def buildingChain(retriever):
    print("Building chain using LCEL.....")

    history = itemgetter("history")
    question = itemgetter("question")
    ragDocs = itemgetter("docs")

    loaded_keys = RunnablePassthrough.assign(
        history=history
    )

    retrieved_documents_chain = {
        "docs": question | retriever,
        "question": question,
        "history": history
    }

    final_inputs = {
        "context": lambda x: combineDocuments(x["docs"]),
        "question": question,
        "history": history
    }

    query_to_llm_chain = {
        "answer": final_inputs | qa_prompt | llm | StrOutputParser(),
        "docs": ragDocs
    }


    return loaded_keys | retrieved_documents_chain | query_to_llm_chain


def CreateChainRag(table):
    print("CreateChain chain creation funtion for table %s", table)
    Settings.llm = llm
    Settings.embed_model=get_embedding()
    if table == "":
        table = "contract_nims"
        logging.info(
            "ERROR: table name is not passed. hence default table ezmeral_unified_analytics is getting created")

    vectorStore = VectorStoreBasedOnTable(table)

    index = VectorStoreIndex.from_vector_store(vector_store=vectorStore)

    # This function is the only place specific to sentence window since SentenceTransformerRerank is used
    indexEngine = sentenceWindowPostProcessorAndReranker(index)

    retriever = LlamaIndexRetriever(index=indexEngine)

    chain = buildingChain(retriever)
    engine = indexEngine

    logging.info("CreateChain: chain created successfully")

    return chain,engine


# preLoadChains loands chain for every product category
def summaryChain():
    summary_chain = (
            ChatPromptTemplate.from_template("rephrase the below into maximum 6 words \n{question}")
            | llm
            | StrOutputParser()
    )
    return summary_chain


def stand_alone_question_chain():
    return (
            PromptTemplate.from_template(stand_alone_question_template)
            | llm
            | StrOutputParser()
    )


def createEIChain():
    return (
            ChatPromptTemplate.from_template(
                "Provided a json data below from a server log file, tell me in detail about the error and how to "
                "resolve it \n{question}")
            | llm
            | StrOutputParser()
    )


def createGenericLLMChain():
    chain = (
            ChatPromptTemplate.from_template(
                "You are a technical assistant for question-answering tasks. You very friendly chatbot designed for "
                "HPE technical support."
                "Strictly Do not use chat history for all types of pleasantries and greetings"
                "question: \n{question}"
                "Chat history: {history}"
                "answer:"
            )
            | llm
            | StrOutputParser()
    )
    return chain


# Populates chainStore. Chainstore is a dictonary of chains based on either product name or utility categories.
def preLoadChains():
    chainStore = {}
    # Fetch all tables from Inventory metadata
    productsTable,mistralProductTable = MetaTableFetch()

    if get_foundation_model_used_for_embedding() == MISTRAL:
        # Create separate chain for every product. Key indicates the product name value is the vector store name
        # mistral has a unique embedding hence mistral and GPT will have its unique embedding and dimensions
        for key, value in mistralProductTable.items():
            chain,engine = CreateChainRag(value)
            chainStore[key] = chain

    else:
        for key, value in productsTable.items():
            chain,engine = CreateChainRag(value)
            chainStore[key] = chain


    # chain for Event Interpretation
    chainStore[eventInterpretation] = createEIChain()

    # chain for creating summary of question received
    chainStore[QuestionSummaryStr] = summaryChain()

    # chain for creating stand alone question using history
    chainStore[StandAloneQuestion] = stand_alone_question_chain();

    # chain for direct LLM calls
    chainStore[GenericQuestions] = createGenericLLMChain()

    logging.info("All chains pre loaded successfully %s", chainStore)
    return chainStore


# sourceURL compares the source info from llamaindex documents and matches with S3 url exposed via CDN
def sourceURL(sourcedocs, docToUrl):
    metaDatalist = set()
    for doc in sourcedocs:
        d = doc.metadata
        page_number = d.get('page_number', 0)
        file_name = d.get('file_name', "")
        url = docToUrl.get(file_name, "https://d2cel7q09kz0pe.cloudfront.net/ABG-redacted.pdf")
        urlWithPageFormat = url + "#page=" + page_number
        metaDatalist.add(urlWithPageFormat)
    return metaDatalist

def get_product_and_chains(message):
    #contracts are defaulted to contract because we ony chat with 1 contract at a time.
    product = os.getenv(CONTRACT)
    chain = chainStore[product]
    qsChain = chainStore[QuestionSummaryStr]
    return product,chain,qsChain


chainStore = preLoadChains()