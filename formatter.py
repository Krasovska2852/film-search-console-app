from prettytable import PrettyTable
from colorama import Fore, Style, init
import re
from datetime import datetime
from typing import Literal

# Initialize colorama
init(autoreset=True)

table_headers = ["Title", "Year", "Rating", "Genre", "Actors"]
colored_headers = [Fore.CYAN + Style.BRIGHT + h + Style.RESET_ALL
                   for h in ["Title", "Year", "Rating", "Genre", "Actors"]]

query_headers = {
    "popular": ["Query", "Count"],
    "recent": ["Query", "Timestamp"]
}
query_colored_headers = {
    "popular": [Fore.CYAN + Style.BRIGHT + h + Style.RESET_ALL for h in ["Query", "Count"]],
    "recent": [Fore.CYAN + Style.BRIGHT + h + Style.RESET_ALL for h in ["Query", "Timestamp"]]
}

def truncate_text(text: str, max_len: int = 85) -> str:
    """
       Truncates long strings (actor lists) to a specified maximum length.
       If the text exceeds `max_len`, it is cut off and '...' is appended.
       Ideal for preventing table layout issues in console output.
       Parameters:
           text (str): The input string to truncate.
           max_len (int): Maximum number of characters before truncation. Default: 85.
       Returns:
           str: Truncated string with '...' if longer than max_len, otherwise the original.
       """
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text

def format_results(results: list[dict] | list[tuple], max_rows: int = 10) -> None:
    """
    Formats and prints film search results as a color-enhanced table.
    Uses PrettyTable to create a clean, left-aligned table with:
    - Colorized headers (cyan + bold)
    - Green borders (+, |, -)
    - Colored MPAA ratings (G=green, PG/R=yellow, NC-17=red)
    - Truncated actor lists (via truncate_text)
    Parameters:
        results (list[dict]): List of movie records.
            Each item must have keys/fields: title, year, rating, genre, actors.
        max_rows (int): Maximum number of rows to display. Default: 10.
    Behavior:
        - If results are empty, prints "No results found." in red.
        - Supports both dict and tuple input formats.
        - Raises ValueError for unsupported types.
    """
    if not results:
        print(Fore.RED + "No results found.")
        return

    # Create table
    table = PrettyTable()
    table.field_names = table_headers
    table.align = "l"

    for movie in results[:max_rows]:
        if isinstance(movie, dict):
            row = [
                movie.get("title", ""),
                movie.get("year", ""),
                color_rating(movie.get("rating", "")),
                movie.get("genre", ""),
                truncate_text(movie.get("actors", ""), max_len=85)
            ]
        elif isinstance(movie, tuple):
            row = list(movie[:5])
            if len(row) > 2:
                row[2] = color_rating(row[2])
            if len(row) > 4:
                row[4] = truncate_text(row[4], max_len=85)
        else:
            raise ValueError("Unsupported data format")
        table.add_row(row)

    # Generates the raw table line
    raw_output = table.get_string()

    # Replaces headers with colored ones
    for raw, colored in zip(table_headers, colored_headers):
        raw_output = raw_output.replace(raw, colored)

    #Border coloring
    border_chars = {'+', '|', '-'}
    colored_output = ''.join(
        Fore.GREEN + c + Style.RESET_ALL if c in border_chars else c
        for c in raw_output
    )
    print(colored_output)


def format_statistics_results(
        queries: list[dict],
        mode: Literal["popular", "recent"] = "popular",
        max_rows: int = 5 ) -> None:
    """Formats and prints search query analytics data (popular queries, recent queries)
    in user-friendly table format.
    Displays either:
        - Top popular queries with their count
        - Most recent queries with timestamps
    Parameters:
        queries (list[dict]): List of query records from MongoDB.
        mode (str): Either 'popular' or 'recent'. Default: 'popular'.
        max_rows (int): Max number of rows to display. Default: 5.
    Raises:
        Prints error if mode is invalid or no results found."""
    if not queries:
        print(Fore.RED + f"No {mode} queries found.")
        return

    if mode == "popular":
        headers = ["Query", "Count"]
        extract_row = lambda q: [
            format_dict({
                "keyword": q["_id"].get("keyword"),
                "genre": q["_id"].get("genre"),
                "year_range": q["_id"].get("year_range")
            }),

            q.get("count", 0)
        ]
    elif mode == "recent":
        headers = ["Query", "Timestamp"]
        extract_row = lambda q: [
            format_dict(q.get("params", {})),
            format_timestamp(q.get("timestamp"))
        ]
    else:
        print(Fore.RED + "Invalid mode. Use 'popular' or 'recent'.")
        return

    table = PrettyTable()
    table.field_names = headers
    table.align = "l"

    for entry in queries[:max_rows]:
        table.add_row(extract_row(entry))
    raw_output = table.get_string()

    # Applies colored headers
    colored_stat_headers = [Fore.CYAN + Style.BRIGHT + h + Style.RESET_ALL for h in headers]
    for raw, colored in zip(headers, colored_stat_headers):
        raw_output = raw_output.replace(raw, colored)

    colored_output = re.sub(r"(\+|\||\-)", Fore.GREEN + r"\1" + Style.RESET_ALL, raw_output)

    title = "Popular Queries:" if mode == "popular" else "Recent Queries:"
    print(f"\n{title}")
    print(colored_output)

def format_dict(d: dict) -> str:
    """ Converts a dictionary of search parameters into a readable comma-separated string.
    Only includes non-empty values for 'keyword', 'genre', and 'year_range'.
    Parameters:
        d (dict): Dictionary with optional keys: keyword, genre, year_range.
    Returns:
        str: Formatted string like 'keyword: Inception, genre: Sci-Fi'."""
    try:
        if not isinstance(d, dict):
            return str(d)

        parts = []
        if "keyword" in d and d["keyword"]:
            parts.append(f"keyword: {d['keyword']}")
        if "genre" in d and d["genre"]:
            parts.append(f"genre: {d['genre']}")
        if "year_range" in d and d["year_range"]:
            parts.append(f"year_range: {d['year_range']}")

        return ", ".join(parts) if parts else str(d)
    except Exception as e:
        return f"Error formatting dict: {e}"

def format_timestamp(ts) -> str:
    """Formats a datetime object or timestamp into a readable string.
    Parameters:
        ts: Can be a datetime object or any printable value.
    Returns:
        str: Formatted as 'YYYY-MM-DD HH:MM:SS' if datetime, else string value or 'N/A'."""
    try:
        if isinstance(ts, datetime):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
        return str(ts or "N/A")
    except Exception as e:
        return f"Error formatting timestamp: {e}"

def color_rating(rating: str) -> str:
    """Applies color to rating values.
    G  → Green
    PG, PG-13, R → Yellow
    NC-17 → Red
    Parameters:
        rating (str): The rating value.
    Returns:
        str: The rating wrapped in colorama color codes."""
    rating_str = str(rating).strip().upper()

    if rating_str == "G":
        return Fore.LIGHTGREEN_EX + rating_str + Style.RESET_ALL
    elif rating_str in {"PG", "PG-13", "R"}:
        return Fore.LIGHTYELLOW_EX + rating_str + Style.RESET_ALL
    elif rating_str == "NC-17":
        return Fore.LIGHTRED_EX + rating_str + Style.RESET_ALL
    else:
        return rating_str


