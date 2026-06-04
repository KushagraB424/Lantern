import os
import sys
from dotenv import load_dotenv

# Ensure the backend directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL is not set.")
    sys.exit(1)

import psycopg
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

def main():
    print("1. Verifying Database Connectivity...")
    try:
        with psycopg.connect(db_url, autocommit=True) as conn:
            print("   -> Connection successful!")
            
            print("2. Enabling pgvector extension...")
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("   -> pgvector enabled successfully!")
            
            print("3. Creating LangGraph Checkpoint Tables...")
            with ConnectionPool(conninfo=db_url, max_size=5, kwargs={"autocommit": True}) as pool:
                checkpointer = PostgresSaver(pool)
                checkpointer.setup()
                print("   -> Checkpoint tables created successfully!")
                
            print("\nDatabase initialization and verifications completed successfully.")
    except Exception as e:
        print(f"ERROR during database setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
