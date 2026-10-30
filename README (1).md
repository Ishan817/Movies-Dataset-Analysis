# Movies Dashboard: PostgreSQL + Power BI

TMDB 5000 movies -> PostgreSQL (normalized tables + reporting views) -> Power BI dashboard.

```
data/tmdb_5000_movies.csv
sql/01_schema.sql      tables (movies, genres, movie_genres, companies, movie_companies)
sql/02_views.sql       vw_* reporting views for Power BI
load_to_postgres.py    cleans CSV and loads everything
POWERBI_SETUP.md       connection steps, DAX measures, page layout
```

Quick start:
```bash
pip install pandas psycopg2-binary
python load_to_postgres.py --dsn "postgresql://postgres:PASSWORD@localhost:5432/movies_db"
```
Then follow POWERBI_SETUP.md.
