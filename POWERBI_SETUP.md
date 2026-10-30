# Power BI Dashboard Setup (PostgreSQL → Power BI Desktop)

Power BI Desktop sirf Windows pe chalta hai. Mac/Linux ho to Power BI Service (browser) + on-premises gateway ya Windows VM chahiye.

## 1. Postgres me data load karo
```bash
pip install pandas psycopg2-binary
# psql / pgAdmin me ek baar:  CREATE DATABASE movies_db;
python load_to_postgres.py --csv data/tmdb_5000_movies.csv \
    --dsn "postgresql://postgres:YOUR_PASSWORD@localhost:5432/movies_db"
```
Ye `sql/01_schema.sql` (tables) aur `sql/02_views.sql` (vw_* views) dono chala deta hai.
Expected: movies 4803, genres 20, movie_genres 12160, companies 5047, movie_companies 13677.

## 2. Power BI se connect
1. Power BI Desktop → **Get data → PostgreSQL database**.
2. Server: `localhost:5432` (ya `localhost`), Database: `movies_db`.
3. **Import** mode select karo (data chhota hai, fast rahega).
4. Credentials: Database tab → user `postgres` + password.
5. Agar "Npgsql" error aaye to Npgsql provider (v4.0.x+) install karo aur Power BI restart karo.
6. Navigator me ye views select karo, phir **Load**:
   - `vw_movie_facts`  (main fact table)
   - `vw_movie_genre`  (movie ↔ genre)
   - `vw_genre_summary`, `vw_year_summary`, `vw_language_summary`, `vw_company_summary`

## 3. Model → Relationships
Model view me:
- `vw_movie_genre[movie_id]` → `vw_movie_facts[movie_id]` (Many-to-one, **Both** cross-filter direction so genre slicer movies ko filter kare)

Summary views standalone rakho (unke apne chart hain). Genre slicer ke liye `vw_movie_genre[genre_name]` use karo.

Column formats: `budget`, `revenue`, `profit` → Whole number, `$#,0`; `release_year`, `decade` → Don't summarize; `roi_pct` → Decimal.

## 4. DAX measures
`vw_movie_facts` table me **New measure** se banao:

```DAX
Movies = COUNTROWS ( vw_movie_facts )

Total Revenue = SUM ( vw_movie_facts[revenue] )
Total Budget  = SUM ( vw_movie_facts[budget] )
Total Profit  = [Total Revenue] - [Total Budget]

Avg Rating =
CALCULATE ( AVERAGE ( vw_movie_facts[vote_average] ), vw_movie_facts[vote_count] >= 10 )

Avg Popularity = AVERAGE ( vw_movie_facts[popularity] )

Profitable Movies =
CALCULATE ( [Movies], vw_movie_facts[outcome] = "Profit" )

Loss Movies =
CALCULATE ( [Movies], vw_movie_facts[outcome] = "Loss" )

Hit Rate % =
DIVIDE ( [Profitable Movies], [Profitable Movies] + [Loss Movies] )

Avg ROI % =
AVERAGEX ( FILTER ( vw_movie_facts, NOT ISBLANK ( vw_movie_facts[roi_pct] ) ), vw_movie_facts[roi_pct] )
```
Dhyan: `Total Profit` ko sirf unhi movies pe sahi dikhana ho jinke budget aur revenue dono known hain, to is version ko use karo:
```DAX
Total Profit = SUM ( vw_movie_facts[profit] )
```
(`profit` column NULL hota hai jab koi ek value unknown ho.)

## 5. Dashboard layout (3 pages)

**Page 1: Overview**
- KPI cards (top row): `Movies`, `Total Revenue`, `Total Profit`, `Avg Rating`, `Hit Rate %`
- Line chart: `release_year` vs `Total Revenue` (from `vw_year_summary`)
- Bar: Top 10 movies by revenue → visual filter *Top N = 10 by revenue* (title on axis)
- Donut: `outcome` (Profit/Loss/Unknown) by `Movies`
- Slicers: `decade`, `original_language`, `genre_name`

**Page 2: Genres & Languages**
- Bar: `vw_genre_summary[genre_name]` vs `movies`
- Bar: genre vs `avg_rating`
- Scatter: x = `avg_popularity`, y = `avg_rating`, size = `movies`, details = `genre_name`
- Bar: top 10 `vw_language_summary` by `movies`  (English 4505 baaki sab se bahut zyada, log scale ya "exclude en" toggle useful)

**Page 3: Profitability**
- Table: Top 10 profitable (title, budget, revenue, profit) → Top N by `profit`
- Table: Biggest flops → filter `budget > 50,000,000` aur `outcome = "Loss"`, Top N bottom 10 by `profit`
- Scatter: `budget` (x) vs `revenue` (y), details = `title`, legend = `outcome`
- Bar: `vw_company_summary` top 10 by `total_revenue`

## 6. Refresh
Data change hone pe `load_to_postgres.py` dubara chalao, phir Power BI me **Home → Refresh**.
Publish karna ho to **Publish** → Power BI Service; scheduled refresh ke liye on-premises gateway chahiye (Postgres local hai to).

## Data notes
- TMDB me budget/revenue = 0 ka matlab "unknown" hai. Isliye DB me wo NULL store hote hain; 4803 me se sirf 3229 movies ke paas dono financials hain.
- Ratings average ke liye `vote_count >= 10` filter lagaya hai, warna 1-2 votes wali movies year/genre averages bigaad deti hain.
- Ek movie ki `release_date` missing hai (release_year NULL), wo year charts me nahi aati.
