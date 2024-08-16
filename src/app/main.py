from src.app.llm import get_llm, get_foundation_model_used_for_embedding, MISTRAL, GPT3, MISTRAL7B, MISTRAL22B, MISTRALAPI
from src.app.logging_config import setup_logging
import logging
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.chatbackendHandlers.corehandler import ask_bob, askLLM
from src.app.utlility import get_product_and_chains, eventInterpretation, QuestionSummaryStr, StandAloneQuestion, \
    sourceURL, chainStore

import time
import math

logger = setup_logging()
load_dotenv()
app = FastAPI()

metaToUrl = {
    "nimcontract.pdf":"https://d2cel7q09kz0pe.cloudfront.net/ABG-redacted.pdf",
}

logger.info("this program will be using foundation model %s", get_llm())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


truEvalRecpordings = []

if chainStore == {}:
    logging.info("ERROR: CRITICAL chain not loaded, hence cant proceed %s", chainStore)
    exit("chain not loaded, hence cant proceed")


@app.post("/api/chat")
async def ask_assistant_for_hpe(request: Request):
    logging.info("entering ask_assistant_for_hpe")
    docs = []
    data = await request.json()
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    start_time = time.time()

    product, chain, qsChain = get_product_and_chains(message)

    history = data.get("chat_history")

    logging.info("product processing %s", product)

    chain = chainStore[product]
    qsChain = chainStore[QuestionSummaryStr]

    logging.info("product processing %s", product)

    responseMsg, summaryResponse, docs, questionSummary, rec, executionTime = ask_bob(chain, qsChain,
                                                                                      message, history, True)

    returnObject = {
        "bot_response": responseMsg,
        "chat_history": summaryResponse
    }

    if len(docs) != 0:
        returnObject['answer_context'] = sourceURL(docs, metaToUrl)

    if history is None:
        returnObject['question_summary'] = questionSummary

    returnObject['response_time'] = math.ceil(time.time() - start_time)

    return returnObject


@app.get("/api/health")
async def health_monitor(request: Request):
    return {"Response": health()}
