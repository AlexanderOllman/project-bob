import logging
import os
import time

from dotenv import load_dotenv
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.runnables import RunnableParallel

from langchain.prompts.prompt import PromptTemplate

from src.app.llm import get_llm

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

load_dotenv()
llm = get_llm()

def health():
    logging.info("in healthcheck")
    return "I am healthy"

def askLLM(chain, qsChain, questionString, chatHistorySummary,create_summary):
    logging.info("askLLM function")

    if chain is None:
        logging.info("chain is None, create one before accessing further")
        return

    if questionString == "":
        logging.info("questionString is empty")
        return

    if chatHistorySummary == {} or chatHistorySummary is None:
        logging.info("chatHistorySummary is empty")
        chatHistorySummary = ''

    parallelChains = RunnableParallel(llmchain=chain, questionSummary=qsChain)
    inputs = {"question": questionString, "history": chatHistorySummary}

    logging.info("askLLM function - invoking log")
    questionSummary,responseSummary = None,None
    startTime = time.time()
    if create_summary and chatHistorySummary == '':
        response = parallelChains.invoke(inputs)
        questionSummary = response['questionSummary']
        llmResponse = response['llmchain']
    else:
        llmResponse = chain.invoke(inputs)
    executionTime = round(time.time() - startTime, 3)
    logging.info("--- Execution time in %s seconds ---" % executionTime)
    logging.info("llmResponse %s", llmResponse)
    if create_summary:
        responseSummary = get_conversation_summary(chatHistorySummary, inputs, llmResponse,200)
    return llmResponse, responseSummary, questionSummary, executionTime


def ask_bob(chain, qsChain, questionString, chatHistorySummary, create_summary):
    logging.info("askJyoti function")
    parallelChains = RunnableParallel(rag=chain, questionSummary=qsChain)
    rec = None
    if chain is None:
        logging.info("chain is None, create one before accessing further")
        return

    if questionString == "":
        logging.info("questionString is empty")
        return

    if chatHistorySummary == {} or chatHistorySummary is None:
        logging.info("chatHistorySummary is empty")
        chatHistorySummary = ''

    inputs = {"question": questionString, "history": chatHistorySummary}
    questionSummary,responseSummary = None,None
    startTime = time.time()

    if create_summary and chatHistorySummary == '':
        response = parallelChains.invoke(inputs)
        questionSummary = response['questionSummary']
        ragResponse = response['rag']
    else:
        ragResponse = chain.invoke(inputs)

    logging.info("full response:%s", ragResponse)
    executionTime = round(time.time() - startTime,3)
    logging.info("--- Execution time in %s seconds ---" % executionTime)

    answer = ragResponse['answer']
    documents = ragResponse['docs']
    if len(documents) == 0 :
        logging.info("No source Docs returned")

    logging.info("count of source documents received:%d",len(documents))

    if create_summary:
        responseSummary = get_conversation_summary(chatHistorySummary, inputs, answer,1000)
    return answer, responseSummary, documents, questionSummary, rec, executionTime


def get_conversation_summary(chatHistorySummary, inputs, answer,tokens_limit):
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=tokens_limit,
        moving_summary_buffer=chatHistorySummary,
    )
    memory.save_context(inputs, {"answer": answer})
    return memory.load_memory_variables({})['history']
