import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import logging
from dotenv import load_dotenv
from llama_index.embeddings.ollama import OllamaEmbedding

logger = logging.getLogger(__name__)

MISTRAL = "MISTRAL"
MISTRALAPI = "MISTRAL_API"
MISTRAL22B = "MISTRAL_22B"
MISTRAL7B = "MISTRAL_7B"
CHATHPE= "CHATHPE"
NIM_KEY="NIM_KEY"
GPT3 = "GPT3"
MISTRAL_NVIDIA = "MISTRAL_NVIDIA"
CONTRACT="CONTRACT"
load_dotenv()



def get_llm():
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    llm = ChatNVIDIA(
            model="meta/llama3-8b-instruct",
            api_key=os.getenv(NIM_KEY),
            temperature=0.2,
            max_tokens=2048,
            top_p=0.7,
        )
    return llm



def get_foundation_model_used_for_embedding():
    if os.getenv("FOUNDATION_MODEL") == GPT3:
        return GPT3
    else:
        return MISTRAL


def get_embedding():

    from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
    return NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-mistral-7b-v2",
            api_key=os.getenv(NIM_KEY),
            embed_batch_size=50,
            truncate="END",
        )



def get_embed_dim():
    if get_foundation_model_used_for_embedding() == GPT3:
        return 1536
    elif get_foundation_model_used_for_embedding() == MISTRAL:
        return 4096 #6144 for mistral 22b and 4096 for mistral7b
    else:  # default embedding is mistral7b
        return 4096
