import logging

from langchain_community.vectorstores.pgvector import PGVector
from llama_index.vector_stores.postgres import PGVectorStore
import psycopg2
from dotenv import load_dotenv
from src.app.llm import get_embed_dim
import os

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

CONNECTION_STRING = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def fetchFromVectorStore(embedding, collection, table):
    logging.info("From PG vector")
    if collection == "":
        collection = "recursive_chunking"
    return PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embedding,
        collection_name="user_guide_recursive",
    )


def VectorStoreBasedOnTable(table_name):
    vector_store = PGVectorStore.from_params(
        database=DB_NAME,
        host=DB_HOST,
        password=DB_PASSWORD,
        port=DB_PORT,
        user=DB_USER,
        table_name=table_name,
        embed_dim=get_embed_dim(),  # openai embedding dimension
    )
    return vector_store


def create_connection():
    try:
        connection = psycopg2.connect(
            database=DB_NAME,
            host=DB_HOST,
            password=DB_PASSWORD,
            port=DB_PORT,
            user=DB_USER,
        )
        return connection
    except psycopg2.Error as e:
        logging.info("Error connecting to PostgreSQL:", e)
        return None


def MetaTableLookup(productName):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        queryStr = (
            "select * from inventory_data where product = '{productName}';".format(
                productName=productName
            )
        )
        logging.info("query string for MetaTableLookup %s", queryStr)
        cursor.execute(queryStr)

        row = cursor.fetchone()
        if len(row) > 0:
            logging.info(row[1])
            return row[1]
        else:
            logging.info("Error")
            return None


def MetaTableFetch():
    conn = create_connection()
    if conn:
        productTable = {}
        mistralProductTable = {}
        cursor = conn.cursor()
        queryStr = "select product, table_name, mistral_table_name from inventory_data WHERE product=\'contract_nims\'"
        print("queryStr",queryStr)
        cursor.execute(queryStr)

        for row in cursor:
            productTable[row[0]] = row[1]
            mistralProductTable[row[0]] = row[2]

        logging.info(productTable)
        logging.info(mistralProductTable)
        # if productTable == {}:
        #     logging.info("ERROR: no data in the table inventory_data")
        return productTable, mistralProductTable
    else:
        logging.error("DB connection failed")
