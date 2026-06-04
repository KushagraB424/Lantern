import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

_pool = None

def get_checkpointer():
    """
    Returns a checkpointer for LangGraph. 
    Uses PostgreSQL if DATABASE_URL is provided, else falls back to MemorySaver.
    """
    global _pool
    db_url = os.getenv("DATABASE_URL")
    
    if db_url:
        if _pool is None:
            _pool = ConnectionPool(
                conninfo=db_url,
                max_size=5,
                min_size=1,
                kwargs={"autocommit": True, "prepare_threshold": 0},
            )
        # We need to setup the checkpointer tables. 
        # In a real app we'd do this on startup via a lifecycle hook, but for simplicity we do it here
        checkpointer = PostgresSaver(_pool)
        checkpointer.setup()
        return checkpointer
    else:
        print("WARNING: DATABASE_URL not set. Falling back to MemorySaver.")
        return MemorySaver()
