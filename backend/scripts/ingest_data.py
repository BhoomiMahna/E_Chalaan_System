import sys
import os

# Add backend directory to python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from langchain.schema import Document
from core.vector_db import vector_db_manager

def ingest_traffic_laws():
    """Ingest dummy traffic laws and regulations into the Vector DB."""
    
    # In a real scenario, this would load from PDFs or scraping.
    # We simulate some foundational laws for the RAG agent to use.
    laws = [
        "The Motor Vehicles Act, 1988: Section 129 mandates the wearing of protective headgear (helmet) for all persons driving or riding a two-wheeled motorcycle. The fine for a first offense is Rs 1000 and disqualification of license for 3 months.",
        "Traffic Signal Rules: Section 119 of the Motor Vehicles Act states that jumping a red light is a punishable offense. The base fine is Rs 5000 and can go up to Rs 10000 depending on the severity and repeated offenses.",
        "Speeding Regulations: Section 112 states that driving at a speed exceeding the maximum limit is punishable under Section 183. Fines vary from Rs 1000 to Rs 2000 for light motor vehicles.",
        "Driving without a License: Section 3 prohibits driving without an effective driving license. Under Section 181, the penalty is a fine of Rs 5000 or imprisonment up to 3 months, or both.",
        "Drunk Driving: Section 185 makes driving by a drunken person or by a person under the influence of drugs punishable by up to Rs 10000 and/or imprisonment."
    ]
    
    documents = [
        Document(page_content=law, metadata={"source": "Motor Vehicles Act, 1988", "type": "law"})
        for law in laws
    ]
    
    print(f"Ingesting {len(documents)} documents into Vector DB...")
    vector_db_manager.add_documents(documents)
    print("Ingestion complete. The RAG pipeline is ready.")

if __name__ == "__main__":
    ingest_traffic_laws()
