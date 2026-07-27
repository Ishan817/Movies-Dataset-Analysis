
-- Top 10 Highest Revenue Movies
SELECT title_x, revenue 
FROM movies 
WHERE revenue > 0 
ORDER BY revenue DESC 
LIMIT 10;

-- Top 10 Most Popular Movies
SELECT title_x, popularity 
FROM movies 
ORDER BY popularity DESC 
LIMIT 10;

-- Average Rating by Year
SELECT year, ROUND(AVG(vote_average)::numeric, 2) as avg_rating
FROM movies 
WHERE year IS NOT NULL
GROUP BY year 
ORDER BY year DESC;

-- Top 10 Most Profitable Movies
SELECT title_x, budget, revenue, 
       (revenue - budget) AS profit
FROM movies 
WHERE budget > 0 AND revenue > 0
ORDER BY profit DESC 
LIMIT 10;

-- Movies Count by Language
SELECT original_language, COUNT(*) as total_movies
FROM movies 
GROUP BY original_language 
ORDER BY total_movies DESC
LIMIT 10;

-- Flop Movies (High Budget Low Revenue)
SELECT title_x, budget, revenue,
       (revenue - budget) AS loss
FROM movies
WHERE budget > 50000000 AND revenue < budget
ORDER BY loss ASC
LIMIT 10;
