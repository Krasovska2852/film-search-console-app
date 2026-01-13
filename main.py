from mysql_connector import search_by_keyword, search_by_genre_and_year, get_all_genres, get_year_range
from log_writer import log_search
from log_stats import get_popular_queries, get_recent_queries
from formatter import format_results, format_statistics_results

def main():
    """
    The main application loop that displays the menu and handles user interaction.
    This function:
    - Displays a menu
    - Processes user input for search and navigation
    - Manages pagination for search results
    - Logs every search to MongoDB via log_writer
    - Formats output using formatter.py
    - Handles invalid input
    The loop continues until the user selects 'Exit'.
    Features:
        - Keyword search with pagination
        - Genre + year search with dynamic input (specific year or range)
        - Display of popular and recent queries from analytics
        - Input validation for genres and years
        - Clean navigation: Previous | Next | Exit
    Example Flow:
        1. User selects "Search by keyword"
        2. Enters "Inception"
        3. Sees first 10 results
        4. Can navigate to next/previous page
        5. Each page view is logged
        6. Returns to menu after exit """

    while True:
        print("\n🎬 Main Menu:")
        print("1. 🔍 Search by keyword")
        print("2. 🎭 Search by genre and release year range")
        print("3. 📈 Show 5 popular queries")
        print("4. 🕒 Show 5 most recent queries")
        print("5. ❌ Exit")

        choice = input("Your choice: ")

        # search by keyword
        if choice == "1":
            keyword = input("Enter a keyword to search for films: ")
            page = 1
            # inner loop for pagination
            while True:
                results = search_by_keyword(keyword, limit=10, offset=(page - 1) * 10)
                format_results(results)
                log_search("keyword", {"keyword": keyword, "page": page +1}, len(results))

                print("\nNavigation: 1 - Previous | 2 - Next | 3 - Exit")
                nav = input("Your choice: ")

                if nav == "3":
                    break
                elif nav == "1":
                    if page > 1:
                        page -= 1
                    else:
                        print("You're already on the first page.")
                elif nav == "2":
                    page += 1
                else:
                    print("Invalid input.")

        # search by genre and year(2 options)
        elif choice == "2":
            print("\n🎭 Available Genres:")
            genres = get_all_genres()
            print(", ".join(genres))

            min_year, max_year = get_year_range()
            print(f"\n📅 Available Year Range: {min_year} to {max_year}\n")

            genre = input("Enter genre name: ").strip()
            if genre not in genres:
                print("The genre input is incorrect.")
                continue

            # year search type selection
            print("\nDo you want to search by:")
            print("1. Specific year")
            print("2. Year range")
            year_choice = input("Your choice: ").strip()
            if year_choice == "1":
                # Specific year search
                while True:
                    try:
                        year = int(input(f"Enter year ({min_year}-{max_year}): "))
                        if min_year <= year <= max_year:
                            year_from = year
                            year_to = year
                            break
                        else:
                            print(f"Year must be between {min_year} and {max_year}")
                    except ValueError:
                        print("Please enter a valid year")

            elif year_choice == "2":
                # Year range search
                while True:
                    try:
                        year_from = int(input(f"Enter start year ({min_year}-{max_year}): "))
                        year_to = int(input(f"Enter end year ({min_year}-{max_year}): "))
                        if not (min_year <= year_from <= max_year) or not (min_year <= year_to <= max_year):
                            print(f"Years must be between {min_year} and {max_year}")
                            continue
                        if year_from > year_to:
                            print("Start year cannot be greater than end year")
                            continue
                        break
                    except ValueError:
                        print("Please enter valid years")
            else:
                print("Invalid choice. Please select 1 or 2")
                continue

            page = 1

            # pagination loop for genre/year search
            while True:
                results = search_by_genre_and_year(genre, year_from, year_to, limit=10, offset=(page - 1) * 10)
                format_results(results)

                # format year to str for further logging
                year_param = str(year_from) if year_choice == "1" else f"{year_from}-{year_to}"
                # log the search with parameters
                log_search("genre_year", {"genre": genre, "year_range": year_param}, len(results))

                print("\nNavigation: 1 - Previous | 2 - Next | 3 - Exit")
                nav = input("Your choice: ")
                if nav == "3":
                    break
                elif nav == "1":
                    if page > 1:
                        page -= 1
                    else:
                        print("You're already on the first page.")
                elif nav == "2":
                    page += 1
                else:
                    print("Invalid input.")

        # show popular queries
        elif choice == "3":
            print("📈 Top 5 popular queries:")
            format_statistics_results(get_popular_queries(), mode="popular") # fetch and format from Mongo

        # show recent queries
        elif choice == "4":
            print("\n🕒 Top 5 recent queries:")
            format_statistics_results(get_recent_queries(), mode="recent") # fetch and format recent searches

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

