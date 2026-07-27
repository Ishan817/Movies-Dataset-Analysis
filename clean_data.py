"""
Movies Dataset Analysis - Data Cleaning
-----------------------------------------
Loads the raw TMDB 5000 movies dataset, cleans it, and engineers the
columns referenced in movies_queries.sql (title_x, year, profit).

Original dataset column is `title`. Because this project originally
merged the movies file with a credits file (both containing a `title`
column), pandas auto-suffixes duplicate columns as title_x / title_y.
We recreate that here by renaming `title` -> `title_x` so the SQL
queries run unmodified.
"""

import pandas as pd
import sqlite3
import os

RAW_PATH = "data/tmdb_5000_movies.csv"
CLEAN_CSV_PATH = "output/movies_cleaned.csv"
DB_PATH = "output/movies.db"


def load_raw(path=RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded raw dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Drop exact duplicate rows and rows with no title at all
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["title"], inplace=True)

    # Parse release_date -> datetime, extract year
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = df["release_date"].dt.year

    # Treat 0s in budget/revenue/runtime as missing (TMDB uses 0 for "unknown")
    for col in ["budget", "revenue", "runtime"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing runtime with the median so aggregate stats aren't skewed
    df["runtime"] = df["runtime"].fillna(df["runtime"].median())

    # Feature engineering
    df["profit"] = df["revenue"] - df["budget"]
    df["title_x"] = df["title"]  # matches the schema movies_queries.sql expects

    # Keep a tidy set of columns for the analysis
    keep_cols = [
        "id", "title_x", "original_title", "original_language", "genres",
        "release_date", "year", "budget", "revenue", "profit", "runtime",
        "popularity", "vote_average", "vote_count", "status", "overview",
        "production_companies", "production_countries", "spoken_languages",
        "tagline", "keywords", "homepage",
    ]
    df = df[[c for c in keep_cols if c in df.columns]]

    print(f"Cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def save_outputs(df: pd.DataFrame):
    os.makedirs("output", exist_ok=True)
    df.to_csv(CLEAN_CSV_PATH, index=False)
    print(f"Saved cleaned CSV -> {CLEAN_CSV_PATH}")

    # Load into SQLite as a stand-in for PostgreSQL so movies_queries.sql
    # can be run directly against a real database table named `movies`.
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("movies", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded table 'movies' into SQLite DB -> {DB_PATH}")


def main():
    df = load_raw()
    df = clean(df)
    save_outputs(df)


if __name__ == "__main__":
    main()
