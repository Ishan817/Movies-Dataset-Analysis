"""
Movies Dataset Analysis
------------------------
Runs the queries in movies_queries.sql against the cleaned movies table
(SQLite stand-in for PostgreSQL) and produces the visualizations used in
the Looker Studio dashboard (revenue, popularity, ratings-by-year,
profitability, language distribution, budget-vs-revenue flops).

Usage:
    python clean_data.py   # run once first to build output/movies.db
    python analysis.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

DB_PATH = "output/movies.db"
CHARTS_DIR = "charts"

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120


def run_query(conn, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # ---------------------------------------------------------------
    # 1. Top 10 Highest Revenue Movies
    # ---------------------------------------------------------------
    top_revenue = run_query(conn, """
        SELECT title_x, revenue
        FROM movies
        WHERE revenue > 0
        ORDER BY revenue DESC
        LIMIT 10;
    """)
    print("\nTop 10 Highest Revenue Movies")
    print(top_revenue.to_string(index=False))

    plt.figure(figsize=(9, 6))
    sns.barplot(data=top_revenue, y="title_x", x="revenue", hue="title_x", palette="viridis", legend=False)
    plt.title("Top 10 Highest Revenue Movies")
    plt.xlabel("Revenue (USD)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/01_top_revenue_movies.png")
    plt.close()

    # ---------------------------------------------------------------
    # 2. Top 10 Most Popular Movies
    # ---------------------------------------------------------------
    top_popular = run_query(conn, """
        SELECT title_x, popularity
        FROM movies
        ORDER BY popularity DESC
        LIMIT 10;
    """)
    print("\nTop 10 Most Popular Movies")
    print(top_popular.to_string(index=False))

    plt.figure(figsize=(9, 6))
    sns.barplot(data=top_popular, y="title_x", x="popularity", hue="title_x", palette="magma", legend=False)
    plt.title("Top 10 Most Popular Movies")
    plt.xlabel("Popularity Score")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/02_top_popular_movies.png")
    plt.close()

    # ---------------------------------------------------------------
    # 3. Average Rating by Year
    # ---------------------------------------------------------------
    avg_rating_by_year = run_query(conn, """
        SELECT year, ROUND(AVG(vote_average), 2) as avg_rating
        FROM movies
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year DESC;
    """)
    print("\nAverage Rating by Year (most recent 10 shown)")
    print(avg_rating_by_year.head(10).to_string(index=False))

    plt.figure(figsize=(10, 5))
    plotdf = avg_rating_by_year.sort_values("year")
    sns.lineplot(data=plotdf, x="year", y="avg_rating", marker="o")
    plt.title("Average Movie Rating by Year")
    plt.xlabel("Year")
    plt.ylabel("Average Rating")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/03_avg_rating_by_year.png")
    plt.close()

    # ---------------------------------------------------------------
    # 4. Top 10 Most Profitable Movies
    # ---------------------------------------------------------------
    top_profit = run_query(conn, """
        SELECT title_x, budget, revenue,
               (revenue - budget) AS profit
        FROM movies
        WHERE budget > 0 AND revenue > 0
        ORDER BY profit DESC
        LIMIT 10;
    """)
    print("\nTop 10 Most Profitable Movies")
    print(top_profit.to_string(index=False))

    plt.figure(figsize=(9, 6))
    sns.barplot(data=top_profit, y="title_x", x="profit", hue="title_x", palette="crest", legend=False)
    plt.title("Top 10 Most Profitable Movies")
    plt.xlabel("Profit (Revenue - Budget, USD)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/04_top_profitable_movies.png")
    plt.close()

    # ---------------------------------------------------------------
    # 5. Movies Count by Language
    # ---------------------------------------------------------------
    lang_count = run_query(conn, """
        SELECT original_language, COUNT(*) as total_movies
        FROM movies
        GROUP BY original_language
        ORDER BY total_movies DESC
        LIMIT 10;
    """)
    print("\nMovies Count by Language (Top 10)")
    print(lang_count.to_string(index=False))

    plt.figure(figsize=(8, 6))
    sns.barplot(data=lang_count, x="original_language", y="total_movies", hue="original_language", palette="flare", legend=False)
    plt.title("Movie Count by Original Language (Top 10)")
    plt.xlabel("Language Code")
    plt.ylabel("Number of Movies")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/05_movies_by_language.png")
    plt.close()

    # ---------------------------------------------------------------
    # 6. Flop Movies (High Budget, Low Revenue)
    # ---------------------------------------------------------------
    flops = run_query(conn, """
        SELECT title_x, budget, revenue,
               (revenue - budget) AS loss
        FROM movies
        WHERE budget > 50000000 AND revenue < budget
        ORDER BY loss ASC
        LIMIT 10;
    """)
    print("\nTop 10 Flop Movies (High Budget, Low Revenue)")
    print(flops.to_string(index=False))

    plt.figure(figsize=(9, 6))
    sns.barplot(data=flops, y="title_x", x="loss", hue="title_x", palette="rocket", legend=False)
    plt.title("Top 10 Flop Movies (Budget > $50M, Revenue < Budget)")
    plt.xlabel("Loss (Revenue - Budget, USD)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/06_flop_movies.png")
    plt.close()

    # ---------------------------------------------------------------
    # Bonus: Budget vs Revenue scatter (dashboard filler chart #7)
    # ---------------------------------------------------------------
    scatter_df = run_query(conn, """
        SELECT budget, revenue
        FROM movies
        WHERE budget > 0 AND revenue > 0;
    """)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=scatter_df, x="budget", y="revenue", alpha=0.4)
    plt.title("Budget vs Revenue (All Movies)")
    plt.xlabel("Budget (USD)")
    plt.ylabel("Revenue (USD)")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/07_budget_vs_revenue.png")
    plt.close()

    conn.close()

    # Save each query's result for the Looker Studio dashboard / GitHub docs
    top_revenue.to_csv("output/top_10_revenue.csv", index=False)
    top_popular.to_csv("output/top_10_popular.csv", index=False)
    avg_rating_by_year.to_csv("output/avg_rating_by_year.csv", index=False)
    top_profit.to_csv("output/top_10_profitable.csv", index=False)
    lang_count.to_csv("output/movies_by_language.csv", index=False)
    flops.to_csv("output/top_10_flops.csv", index=False)

    print(f"\nAll charts saved to '{CHARTS_DIR}/', all query results saved to 'output/'.")


if __name__ == "__main__":
    main()
