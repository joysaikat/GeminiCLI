import os
import shutil
import argparse
from ingest import ingest_docs

def clear_database(db_path="vector_db"):
    """Deletes the vector database folder."""
    if os.path.exists(db_path):
        print(f"Clearing database at {db_path}...")
        shutil.rmtree(db_path)
        print("Database cleared.")
    else:
        print("No database found to clear.")

def refresh_knowledge():
    """Clears and re-ingests documents."""
    clear_database()
    ingest_docs()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the RAG Vector Database")
    parser.add_update_topic = parser.add_mutually_exclusive_group()
    
    parser.add_argument("action", choices=["clear", "ingest", "refresh"], 
                        help="Action to perform: 'clear' (delete DB), 'ingest' (add new docs), 'refresh' (rebuild DB)")

    args = parser.parse_args()

    if args.action == "clear":
        clear_database()
    elif args.action == "ingest":
        ingest_docs()
    elif args.action == "refresh":
        refresh_knowledge()
