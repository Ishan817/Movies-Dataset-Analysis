# Movies Dataset Analysis

Cleaned and analyzed 4,800+ movie records (TMDB 5000 Movies dataset) using
Pandas, Matplotlib, Seaborn, and SQL to surface statistical trends across
genre, revenue, and ratings — built to power a 6+ visualization interactive
Looker Studio dashboard for non-technical stakeholders.

## Tech Stack
- **Python**: Pandas, Matplotlib, Seaborn
- **SQL**: PostgreSQL-style queries (`movies_queries.sql`), executed here
  via SQLite for a fully self-contained, one-command run
- **Google Looker Studio**: dashboard built on the exported query results

## Project Structure
```
movies-dataset-analysis/
├── data/
│   └── tmdb_5000_movies.csv       # raw TMDB 5000 Movies dataset
├── clean_data.py                  # data cleaning + feature engineering
├── movies_queries.sql             # core SQL analysis queries
├── analysis.py                    # runs queries + generates all charts
├── charts/                        # generated visualizations (PNG)
├── output/                        # cleaned CSV, SQLite DB, query result CSVs
└── README.md
```

## How to Run
```bash
pip install pandas matplotlib seaborn

python clean_data.py    # cleans raw data, engineers year/profit columns,
                         # builds a local SQLite DB (output/movies.db)

python analysis.py      # runs movies_queries.sql against the DB, prints
                         # results, and saves charts to charts/
```

## Analysis Performed
1. **Top 10 Highest Revenue Movies**
2. **Top 10 Most Popular Movies** (TMDB popularity score)
3. **Average Rating by Year** (rating trend over time)
4. **Top 10 Most Profitable Movies** (revenue − budget)
5. **Movie Count by Original Language**
6. **Flop Movies** — high budget (>$50M), revenue below budget
7. Bonus: Budget vs. Revenue scatter plot across all movies

All query outputs are exported as CSVs in `output/` and were used as the
data source for the Looker Studio dashboard.

## Data Source
[TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
(via Kaggle).

## Author
Ishan Srivastava — [GitHub](https://github.com/Ishan817)
