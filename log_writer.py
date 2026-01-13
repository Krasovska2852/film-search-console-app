import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

# Global MongoDB connection
_mongo_client = None
_mongo_collection = None


def _get_mongo_collection():
    """Initializes and returns a MongoDB collection instance with connection reuse.
    This is a private helper function (indicated by leading underscore) used internally
    to establish and reuse a single connection to MongoDB for logging. It:
    - Avoids reconnecting on every log attempt.
    - Uses a write-optimized URL (`MONGODB_URL_WRITE`).
    - Tests connectivity before use.
    - Handles errors gracefully and returns None if connection fails.
    Returns:
        Collection: MongoDB collection object if successful, otherwise None."""
    global _mongo_client, _mongo_collection

    if _mongo_collection is not None:
        return _mongo_collection

    try:
        _mongo_client = MongoClient(
            os.getenv("MONGODB_URL_WRITE"),
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        _mongo_client.server_info()
        _mongo_collection = _mongo_client[
            os.getenv("MONGO_DB_NAME")
        ][
            os.getenv("MONGO_COLLECTION_NAME")
        ]
        return _mongo_collection
    except PyMongoError as e:
        print(f"MongoDB connection error: {e}")
        return None


def log_search(
        search_type: str,
        params: dict[str, Any],
        results_count: int
) -> bool:
    """Logs a user search query to MongoDB for later analytics.
    Stores a document containing:
        - timestamp (UTC)
        - search_type (e.g., "keyword", "genre_year")
        - params (search parameters like keyword, genre)
        - results_count (number of films found)
    This data is used to generate statistics like "Top 5 Popular Queries".
    Parameters:
        search_type (str): Type of search, e.g., "keyword" or "genre_year".
        params (dict[str, Any]): Dictionary of search parameters (e.g., {"keyword": "Inception", "page": 1}).
        results_count (int): Number of results returned by the search.
    Returns:
        bool: True if the log was successfully inserted, False otherwise."""
    collection = _get_mongo_collection()
    if collection is None:
        return False

    try:
        doc = {
            "timestamp": datetime.utcnow(),
            "search_type": search_type,
            "params": params,
            "results_count": results_count
        }
        result = collection.insert_one(doc)
        return result.acknowledged
    except PyMongoError as e:
        print(f"Failed to log search: {e}")
        return False

def close_connection():
    """Safely closes the MongoDB connection when the application exits.
    This function:
        - Closes the active MongoDB client connection.
        - Clears global variables to allow fresh connection on restart.
        - Is designed to be called once at shutdown (e.g., in main.py after menu loop)."""
    global _mongo_client, _mongo_collection

    if _mongo_client is not None:
        try:
            _mongo_client.close()
        except Exception as e:
            pass
        finally:
            # Reset global variables
            _mongo_client = None
            _mongo_collection = None