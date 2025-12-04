"""
Docstring for agent.document_ingestion.main
"""
import datetime
import os
from os import path
from typing import Dict, List
import logging
import oci
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import DatabaseClient
from generative_ai import GenerativeAIClient
load_dotenv()

logger = logging.getLogger("OCI Agent")
logging.basicConfig(level=logging.INFO)

FILES_DIR = "files"

def load_and_split_documents_in_chunks(docs: List[str]) -> Dict:
    """"
    Load documents and split them into chunks.
    """

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    today = datetime.date.today()

    results = {}
    for doc in docs:
        file_extension = doc.split('.')[-1].lower()
        if file_extension == 'pdf':

            loader = PyPDFLoader(doc, mode="single")
            pages = loader.load_and_split(text_splitter=text_splitter)
            
            creation_date = pages[0].metadata["creationdate"] if pages else today.isoformat()
            mod_date = pages[0].metadata["moddate"] if pages else today.isoformat()
            results[doc] = {"creation_date": creation_date, "mod_date": mod_date, "content": [page.page_content for page in pages]}
    return results

def embed_summaries(ai_embeddings_client: GenerativeAIClient, summaries: Dict) -> None:
    """
    Placeholder function to embed chunks into a vector database.
    """
    embeddings = {}
    for doc, summaries_list in summaries.items():
        print(f"Embedding {len(summaries_list)} chunks from document: {doc}")
        texts = summaries_list
        doc_embeddings = ai_embeddings_client.get_embeddings(texts)
        embeddings[doc] = doc_embeddings
    return embeddings

def save_chunks_embeddings_and_summaries_in_db(db_client, chunks: Dict, embeddings: Dict, summaries: Dict) -> None:
    """
    Placeholder function to save chunks and metadata to a database.
    """
    sql_for_insertion = open("sqls/insert.sql").read().strip()
    for doc, data in chunks.items():
        doc_embeddings = embeddings[doc]
        doc_summaries = summaries[doc]
        cont = 0
        for i, chunk_text in enumerate(data['content']):
            embedding_vector = doc_embeddings[i]
            summary = doc_summaries[i]
            embedding_vector_str = "[" + ",".join(str(x) for x in embedding_vector) + "]"
            
            creation_date = datetime.datetime.fromisoformat(data['creation_date'].replace("Z", "+00:00"))

            modification_date = datetime.datetime.fromisoformat(data['mod_date'].replace("Z", "+00:00"))

            db_client.execute_query(
                sql_for_insertion,
                {
                    "source_file": doc,
                    "chunk_text": chunk_text,
                    "embedding": embedding_vector_str,
                    "summary": summary,
                    "doc_type": None,
                    "full_metadata": None,
                    "created_on": creation_date,
                    "modified_on": modification_date,
                }
            )
            cont += 1
    return cont

def summarize_chunks(ai_client: GenerativeAIClient, chunks: Dict) -> None:
    """
    Placeholder function to summarize chunks using Generative AI.
    """
    summaries = {}
    for doc, data in chunks.items():
        print(f"Summarizing {len(data['content'])} chunks from document: {doc}")
        texts = data['content']
        doc_summaries = []
        for text in texts:
            response = ai_client.generate(
                f"Resume el siguiente texto: \n\n{text}")
            doc_summaries.append(response.content.strip())
        summaries[doc] = doc_summaries
    return summaries

if __name__ == "__main__":
    files = [path.join(FILES_DIR, f) for f in os.listdir(FILES_DIR) if path.isfile(path.join(FILES_DIR, f))]
    
    db_client = DatabaseClient()
    if db_client.check_connection(): 
        logger.info("Database connection successful.")

    ai_client = GenerativeAIClient()
    if ai_client.check_connection("Testing Generative AI Embeddings Client"):
        logger.info("Generative AI Embeddings Client connection successful.")

    # Create table if not exists
    try:
        create_table_sql = open("sqls/create.sql").read().strip()
        db_client.execute_query(create_table_sql)
    except Exception as e:
        logger.info(f"Omitting table creation: {e}")
    chunks = load_and_split_documents_in_chunks(files)
    summarized_chunks = summarize_chunks(ai_client, chunks)
    embeddings = embed_summaries(ai_client, summarized_chunks)
    save_chunks_embeddings_and_summaries_in_db(db_client, chunks, embeddings, summarized_chunks)