# Film search queries
SEARCH_BY_KEYWORD = """
    SELECT 
        f.title,
        f.release_year AS year,
        f.rating,
        c.name AS genre,
        GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) 
                    ORDER BY a.last_name
                    SEPARATOR ', ') AS actors
    FROM film f
    JOIN film_category fc USING(film_id)
    JOIN category c USING(category_id)
    JOIN film_actor fa USING(film_id)
    JOIN actor a USING(actor_id)
    WHERE f.title LIKE %s
    GROUP BY f.film_id
    ORDER BY f.title
    LIMIT %s OFFSET %s
"""

SEARCH_BY_GENRE_AND_YEAR = """
    SELECT 
        f.title,
        f.release_year AS year,
        f.rating,
        c.name AS genre,
        GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) 
                    ORDER BY a.last_name
                    SEPARATOR ', ') AS actors
    FROM film f
    JOIN film_category fc USING(film_id)
    JOIN category c USING(category_id)
    JOIN film_actor fa USING(film_id)
    JOIN actor a USING(actor_id)
    WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
    GROUP BY f.film_id
    ORDER BY f.release_year, f.title
    LIMIT %s OFFSET %s
"""

GET_ALL_GENRES = "SELECT name FROM category ORDER BY name"

GET_YEAR_RANGE = "SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year FROM film"