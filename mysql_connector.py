import os
import pymysql
from pymysql.connections import Connection
from pymysql.err import MySQLError
from dotenv import load_dotenv
import sql_queries as q

load_dotenv()


def get_db_connection() -> Connection | None:
    """Creates and returns a connection to the MySQL database.
    Uses environment variables (from .env) for host, user, password, and database name.
    Configures the connection to return results as dictionaries (via DictCursor).
    Returns:
        Connection: A pymysql Connection object if successful.
        None: If connection fails (e.g., wrong credentials, server down).
    Notes:
        - Uses `DictCursor` so query results are returned as dicts, not tuples.
        - Connection errors are caught and logged; the app continues running.
        - Not thread-safe by default, but sufficient for CLI usage."""
    try:
        return pymysql.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database"),
            cursorclass=pymysql.cursors.DictCursor
        )
    except MySQLError as e:
        print(f"Database connection error: {e}")
        return None


def execute_query(query: str, params: tuple = (), fetch_all: bool = True) -> list[dict]:
    """Executes a parameterized SQL query safely and returns results.
    This is the core function for all database interactions. It:
    - Uses parameter binding to prevent SQL injection.
    - Handles connection lifecycle (open → execute → close).
    - Returns data as a list of dictionaries.
    Parameters:
        query (str): The SQL query string (with %s placeholders).
        params (tuple): Values to safely substitute into the query.
        fetch_all (bool): If True, returns all rows; if False, returns only the first row.
    Returns:
        list[dict]: Query results as a list of dictionaries. Empty list on error or no results."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall() if fetch_all else cursor.fetchone()
    except MySQLError as e:
        print(f"Query execution error: {e}")
        return []
    finally:
        conn.close()


def search_by_keyword(keyword: str, limit: int = 10, offset: int = 0) -> list[dict]:
    """ Searches for films by keyword in title (via SQL LIKE).
    Supports pagination using LIMIT and OFFSET.
    Parameters:
        keyword (str): The search term.
        limit (int): Number of results per page. Default: 10.
        offset (int): Number of results to skip (for pagination). Default: 0.
    Returns:
        list[dict]: List of matching films with fields like title, year, rating, etc.
    SQL:
        Uses `q.SEARCH_BY_KEYWORD` — query"""
    return execute_query(
        q.SEARCH_BY_KEYWORD,
        ("%"+keyword+"%", limit, offset)
    )

def search_by_genre_and_year(
        genre: str,
        year_from: int,
        year_to: int,
        limit: int = 10,
        offset: int = 0
) -> list[dict]:
    """Searches for films by genre and release year range, with pagination.
    Parameters:
        genre (str): The film genre (e.g., "Action", "Sci-Fi").
        year_from (int): Start year (inclusive).
        year_to (int): End year (inclusive).
        limit (int): Number of results per page. Default: 10.
        offset (int): Offset for pagination. Default: 0.
    Returns:
        list[dict]: List of matching films.
    SQL:
        Uses `q.SEARCH_BY_GENRE_AND_YEAR`"""
    return execute_query(
        q.SEARCH_BY_GENRE_AND_YEAR,
        (genre, year_from, year_to, limit, offset)
    )

def get_all_genres() -> list[str]:
    """Retrieves all unique film genres from the database.
    Used in the main menu to show users what genres are available.
    Returns:
        list[str]: Sorted list of genre names (e.g., ["Action", "Drama", "Sci-Fi"]).
                 Returns empty list if no genres or on error."""
    result = execute_query(q.GET_ALL_GENRES)
    return [row['name'] for row in result] if result else []


def get_year_range() -> tuple[int, int]:
    """Gets the minimum and maximum release years from the films in the database.
    Used to validate user input when searching by year.
    Returns:
        tuple[int, int]: (min_year, max_year), e.g., (1900, 2025).
                       Returns (0, 0) if no data or on error."""
    result = execute_query(q.GET_YEAR_RANGE, fetch_all=False)
    return (result['min_year'], result['max_year']) if result else (0, 0)