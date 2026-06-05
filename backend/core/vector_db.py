import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import Config

class VectorDBManager:
    def __init__(self):
        self.persist_directory = Config.VECTOR_DB_PATH
        # Initialize HuggingFace embeddings locally
        self.embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        
        # Ensure the directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize Chroma vector store
        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="traffic_laws_and_reports"
        )
    
    def add_documents(self, documents):
        """Add documents to the vector DB."""
        self.vector_db.add_documents(documents)
    
    def get_retriever(self, search_kwargs=None):
        """Get the retriever interface."""
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        return self.vector_db.as_retriever(search_kwargs=search_kwargs)

# Singleton instance
vector_db_manager = VectorDBManager()
