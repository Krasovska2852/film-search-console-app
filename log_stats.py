import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

load_dotenv()

# Global MongoDB connection
_mongo_client = None
_mongo_collection = None


def _get_mongo_collection():
    """Initializes and returns a MongoDB collection instance with connection reuse.
    This is a private helper function (prefixed with underscore) that:
    - Creates a single, reusable connection to MongoDB.
    - Caches the connection and collection to avoid reconnecting on every call.
    - Uses a read-only URL (MONGODB_URL_READ) for analytics queries.
    - Tests connectivity before use to catch issues early.
    - Handles errors gracefully and returns None if connection fails.
    Returns:
        Collection: MongoDB collection object if successful, otherwise None."""
    global _mongo_client, _mongo_collection

    if _mongo_collection is not None:
        return _mongo_collection

    try:
        _mongo_client = MongoClient(
            os.getenv("MONGODB_URL_READ"),
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


def get_popular_queries(limit: int = 5) -> list[dict]:
    """Retrieves the most frequently used search combinations from the logs.
    Groups queries by their search parameters (keyword, genre, year_range),
    counts occurrences, and returns the top N most popular ones.
    Parameters:
        limit (int): Maximum number of results to return. Default: 5.
    Returns:
        list[dict]: List of documents.
    MongoDB Pipeline:
        1. $group → groups by params, counts occurrences
        2. $sort → descending by count
        3. $limit → limits to top N"""
    collection = _get_mongo_collection()
    if collection is None:
        return []

    pipeline = [
        {
            "$group": {
                "_id": {
                    "keyword": "$params.keyword",
                    "genre": "$params.genre",
                    "year_range": "$params.year_range"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    try:
        return list(collection.aggregate(pipeline))
    except PyMongoError as e:
        print(f"Failed to get popular queries: {e}")
        return []


def get_recent_queries(limit: int = 5) -> list[dict]:
    """Retrieves the most recently performed search queries.
    Fetches the latest N search logs sorted by timestamp in descending order.
    Parameters:
        limit (int): Number of recent queries to return. Default: 5.
    Returns:
        list[dict]: List of the most recent search log entries.
    Query Logic:
        - find() → retrieves all documents
        - sort("timestamp", -1) → newest first
        - limit(N) → restricts result size"""
    collection = _get_mongo_collection()
    if collection is None:  # Correct None check
        return []

    try:
        return list(collection.find()
                    .sort("timestamp", -1)
                    .limit(limit))
    except PyMongoError as e:
        print(f"Failed to get recent queries: {e}")
        return []