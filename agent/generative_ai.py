from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain.messages import AIMessage, HumanMessage, SystemMessage

import os
from dotenv import load_dotenv

load_dotenv()



class GenerativeAIClient:
    def __init__(self):
        
        self.embeddings_client = OCIGenAIEmbeddings(
            model_id=os.environ["EMBED_MODEL_ID"],
            service_endpoint=os.environ["AI_SERVICE_ENDPOINT"],
            compartment_id=os.environ["OCI_COMPARTMENT_ID"],
        )

        self.generative_ai_client = ChatOCIGenAI(
            model_id=os.environ["GENAI_MODEL_ID"],
            service_endpoint=os.environ["AI_SERVICE_ENDPOINT"],
            compartment_id=os.environ["OCI_COMPARTMENT_ID"],
            model_kwargs={"temperature": 0, "max_tokens": 2000},
        )


    def get_embeddings(self, texts):
        return self.embeddings_client.embed_documents(texts)
    
    def check_connection(self, sample_text="Test connection"):
        # Simple method to check if the client is set up correctly
        try:
            test_embedding = self.embeddings_client.embed_query(sample_text)
            return test_embedding
        except Exception as e:
            print(f"Connection check failed: {e}")
            return False
        
    def generate(self, prompt):
        messages = [
            # SystemMessage(content="your are an AI assistant."),
            # AIMessage(content="Hi there human!"),
            HumanMessage(content=prompt),
        ]
        response = self.generative_ai_client.invoke(messages)
        return response