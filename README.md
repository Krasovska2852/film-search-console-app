# film-search-console-app

Interactive Python command-line application (CLI) to search and explore movies from the Sakila MySQL database.  
The application also **logs all search queries in MongoDB** and provides basic statistics on popular searches.

---

## Features

### 1. Search Movies

- **By title**  
  - Returns up to 10 movies at a time.  
  - Users can request the next 10 results until all results are shown.

- **By genre and release year**  
  - Displays a list of all genres from the database.  
  - Shows minimum and maximum release year available.  
  - Users can specify a range (e.g., 1990–2020) or a specific year.  
  - Results are displayed 10 movies at a time.

---

### 2. Query Logging

- All search queries are saved in **MongoDB** in the collection:  
  `final_project_<your_group>_<your_full_name>`  
- Enables tracking and analysis of user searches.

---

### 3. Statistics

- Displays the **top 5 popular search queries** based on frequency and recent searches.

---

## Technologies

- **Python 3.12.8**  
- **MySQL** (Sakila movie database)  
- **MongoDB** (query logging and statistics)  
- **pymysql**, **pymongo**, and other Python modules (for CLI interface)

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Krasovsak2852/film_search_consol_app.git
cd film_search_consol_app

