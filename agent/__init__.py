from typing import Any, List
from langchain_community.document_loaders import PyPDFLoader

def process_documents(docs: List[str]) -> dict:
    results = {}
    for doc in docs:
        file_extension = doc.split('.')[-1].lower()
        if file_extension == 'pdf':
            loader = PyPDFLoader(doc)
            pages = loader.load_and_split()
            results[doc] = [page.page_content for page in pages]
    return results