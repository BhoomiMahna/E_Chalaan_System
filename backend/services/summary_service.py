from core.local_llm import get_local_llm
from langchain_core.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        try:
            self.llm = get_local_llm()
            self.prompt = PromptTemplate(
                input_variables=["data"],
                template="Analyze the following traffic violation data and provide a concise summary with 3 key insights:\n\n{data}\n\nSummary:"
            )
            self.chain = self.prompt | self.llm
        except Exception as e:
            logger.error(f"Failed to initialize Summary Service: {e}")
            self.chain = None

    def generate_summary(self, data_str: str) -> str:
        """Generate a natural language summary from data."""
        if not self.chain:
            return "Summary generation unavailable. Ensure the local LLM is running."
        try:
            return self.chain.invoke({"data": data_str})
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Failed to generate summary due to an internal error."
