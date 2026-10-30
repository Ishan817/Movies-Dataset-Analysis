"""
Load TMDB 5000 movies into PostgreSQL (schema + views included).

Usage:
    pip install pandas psycopg2-binary
    python load_to_postgres.py --csv data/tmdb_5000_movies.csv \
        --dsn "postgresql://postgres:YOUR_PASSWORD@localhost:5432/movies_db"

The DSN can also come from the DATABASE_URL environment variable.
The database (movies_db) must already exist:  CREATE DATABASE movies_db;
"""

import argparse
import json
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

SQL_DIR = Path(__file__).parent / "sql"


def parse_json_list(value):
    """TMDB stores lists as JSON strings; return [] on bad/empty values."""
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except (TypeError, ValueError):
        return []


def none_if_nan(v):
    return None if pd.isna(v) else v


def prepare(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.drop_duplicates(subset="id").dropna(subset=["title"]).copy()

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year

    # TMDB uses 0 for "unknown" -> store as NULL so averages/profit aren't skewed
    for col in ("budget", "revenue"):
        df[col] = df[col].where(df[col] > 0)
    df["runtime"] = df["runtime"].where(df["runtime"] > 0)

    movies = []
    for r in df.itertuples(index=False):
        movies.append((
            int(r.id), r.title, r.original_title, r.original_language,
            None if pd.isna(r.release_date) else r.release_date.date(),
            None if pd.isna(r.release_year) else int(r.release_year),
            r.status,
            None if pd.isna(r.budget) else int(r.budget),
            None if pd.isna(r.revenue) else int(r.revenue),
            none_if_nan(r.runtime), none_if_nan(r.popularity),
            none_if_nan(r.vote_average), int(r.vote_count),
            none_if_nan(r.tagline), none_if_nan(r.overview),
        ))

    genres, movie_genres = {}, set()
    companies, movie_companies = {}, set()
    for r in df.itertuples(index=False):
        for g in parse_json_list(r.genres):
            genres[g["id"]] = g["name"]
            movie_genres.add((int(r.id), g["id"]))
        for c in parse_json_list(r.production_companies):
            companies[c["id"]] = c["name"]
            movie_companies.add((int(r.id), c["id"]))

    return movies, genres, movie_genres, companies, movie_companies


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/tmdb_5000_movies.csv")
    ap.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args()
    if not args.dsn:
        raise SystemExit("Provide --dsn or set DATABASE_URL")

    movies, genres, movie_genres, companies, movie_companies = prepare(args.csv)

    conn = psycopg2.connect(args.dsn)
    try:
        with conn, conn.cursor() as cur:
            cur.execute((SQL_DIR / "01_schema.sql").read_text(encoding="utf-8"))

            execute_values(cur, """
                INSERT INTO movies (movie_id, title, original_title, original_language,
                    release_date, release_year, status, budget, revenue, runtime_min,
                    popularity, vote_average, vote_count, tagline, overview)
                VALUES %s""", movies, page_size=1000)
            execute_values(cur, "INSERT INTO genres VALUES %s", sorted(genres.items()))
            execute_values(cur, "INSERT INTO movie_genres VALUES %s", sorted(movie_genres))
            execute_values(cur, "INSERT INTO companies VALUES %s", sorted(companies.items()),
                           page_size=1000)
            execute_values(cur, "INSERT INTO movie_companies VALUES %s", sorted(movie_companies),
                           page_size=1000)

            cur.execute((SQL_DIR / "02_views.sql").read_text(encoding="utf-8"))

        with conn.cursor() as cur:
            for t in ("movies", "genres", "movie_genres", "companies", "movie_companies"):
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                print(f"{t:<17} {cur.fetchone()[0]:>7} rows")
        print("Done. Connect Power BI to the vw_* views.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
