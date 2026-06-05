from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from core.local_llm import get_local_llm
from core.vector_db import vector_db_manager
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        try:
            self.llm = get_local_llm()
            self.retriever = vector_db_manager.get_retriever()
            
            # Define the RAG prompt template
            self.prompt = ChatPromptTemplate.from_template(
                "You are an AI Traffic E-Challan assistant. Answer the question based ONLY on the following context. "
                "If you cannot answer the question based on the context, say 'I don't have enough information to answer that based on the provided records and rules.'\n\n"
                "Context: {context}\n\n"
                "Question: {question}\n\n"
                "Answer:"
            )
            
            # Build the RAG chain
            self.chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            self.chain = None

    def ask(self, question: str) -> str:
        """Query the RAG pipeline with a natural language question."""
        if not self.chain:
            return "RAG service is currently unavailable. Ensure the local LLM and Vector DB are configured."
        
        try:
            response = self.chain.invoke(question)
            return response
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return f"Error processing query: {str(e)}"
