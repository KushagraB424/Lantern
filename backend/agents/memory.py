import os
import uuid
import psycopg
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_core.documents import Document
from agents.llm_provider import get_embeddings

load_dotenv()

db_url = os.getenv("DATABASE_URL")
collection_name = "lantern_reports"

def _setup_vector_extension():
    if not db_url:
        return
    try:
        with psycopg.connect(db_url, autocommit=True) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    except Exception as e:
        print(f"Warning: Could not setup pgvector extension: {e}")

_setup_vector_extension()

def get_vector_store():
    if not db_url:
        print("Warning: DATABASE_URL not set, memory features will be disabled.")
        return None
        
    embeddings = get_embeddings(provider="google", model_name="models/gemini-embedding-2")
    
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=db_url,
        use_jsonb=True,
    )

def save_report_to_memory(dataset_id: str, report_text: str, summary: str, quality_score: int):
    store = get_vector_store()
    if not store:
        return False
        
    doc = Document(
        page_content=report_text,
        metadata={
            "dataset_id": dataset_id,
            "summary": summary,
            "quality_score": quality_score
        }
    )
    
    try:
        store.add_documents([doc], ids=[str(uuid.uuid4())])
        return True
    except Exception as e:
        print(f"Error saving to memory: {e}")
        return False

def semantic_search_reports(query: str, limit: int = 5):
    store = get_vector_store()
    if not store:
        return []
        
    try:
        # Returns List[Tuple[Document, float]]
        results = store.similarity_search_with_score(query, k=limit)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "dataset_id": doc.metadata.get("dataset_id"),
                "summary": doc.metadata.get("summary", ""),
                "quality_score": doc.metadata.get("quality_score", 0),
                "report_text": doc.page_content,
                "similarity_score": float(score)
            })
        return formatted_results
    except Exception as e:
        print(f"Error searching memory: {e}")
        return []
