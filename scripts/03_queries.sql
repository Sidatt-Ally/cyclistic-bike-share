-- ============================================================
-- 03_queries.sql — Cyclistic Case Study
-- Requêtes SQL équivalentes à l'analyse Python (03_analysis.py)
-- Table source : cyclistic_clean
-- ============================================================

-- ── 1. Vue d'ensemble : nombre total de trajets par type ─────────────────────
-- Compatibilité : PERCENTILE_CONT = PostgreSQL / BigQuery / SQL Server / DuckDB
--                 Remplacer par MEDIAN() pour SQLite ou MySQL 8.0+
SELECT
    member_casual,
    COUNT(*)                                                        AS total_rides,
    ROUND(AVG(ride_length), 2)                                      AS avg_ride_length_min,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP
          (ORDER BY ride_length), 2)                                AS median_ride_length_min,
    ROUND(MAX(ride_length), 2)                                      AS max_ride_length_min,
    ROUND(MIN(ride_length), 2)                                      AS min_ride_length_min,
    ROUND(STDDEV(ride_length), 2)                                   AS std_ride_length_min
FROM cyclistic_clean
GROUP BY member_casual
ORDER BY member_casual;


-- ── 2. Durée moyenne par jour de la semaine et type d'utilisateur ────────────
-- day_of_week : 1=Dimanche, 7=Samedi
SELECT
    member_casual,
    day_of_week,
    CASE day_of_week
        WHEN 1 THEN 'Dimanche'
        WHEN 2 THEN 'Lundi'
        WHEN 3 THEN 'Mardi'
        WHEN 4 THEN 'Mercredi'
        WHEN 5 THEN 'Jeudi'
        WHEN 6 THEN 'Vendredi'
        WHEN 7 THEN 'Samedi'
    END                             AS day_name,
    COUNT(*)                        AS total_rides,
    ROUND(AVG(ride_length), 2)      AS avg_ride_length_min
FROM cyclistic_clean
GROUP BY member_casual, day_of_week
ORDER BY member_casual, day_of_week;


-- ── 3. Nombre de trajets par mois et type d'utilisateur ─────────────────────
SELECT
    member_casual,
    year,
    month,
    COUNT(*)                        AS total_rides,
    ROUND(AVG(ride_length), 2)      AS avg_ride_length_min
FROM cyclistic_clean
GROUP BY member_casual, year, month
ORDER BY member_casual, year, month;


-- ── 4. Trajets par saison ─────────────────────────────────────────────────────
SELECT
    member_casual,
    season,
    COUNT(*)                        AS total_rides,
    ROUND(AVG(ride_length), 2)      AS avg_ride_length_min,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY member_casual), 1)
                                    AS pct_of_user_type
FROM cyclistic_clean
GROUP BY member_casual, season
ORDER BY member_casual,
    CASE season
        WHEN 'Spring' THEN 1
        WHEN 'Summer' THEN 2
        WHEN 'Fall'   THEN 3
        WHEN 'Winter' THEN 4
    END;


-- ── 5. Types de vélos utilisés ───────────────────────────────────────────────
SELECT
    member_casual,
    rideable_type,
    COUNT(*)                        AS total_rides,
    ROUND(AVG(ride_length), 2)      AS avg_ride_length_min,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY member_casual), 1)
                                    AS pct_of_user_type
FROM cyclistic_clean
GROUP BY member_casual, rideable_type
ORDER BY member_casual, total_rides DESC;


-- ── 6. Top 10 stations de départ — membres ───────────────────────────────────
SELECT
    start_station_name,
    COUNT(*)                        AS total_rides
FROM cyclistic_clean
WHERE member_casual = 'member'
  AND start_station_name IS NOT NULL
GROUP BY start_station_name
ORDER BY total_rides DESC
LIMIT 10;


-- ── 7. Top 10 stations de départ — casual ────────────────────────────────────
SELECT
    start_station_name,
    COUNT(*)                        AS total_rides
FROM cyclistic_clean
WHERE member_casual = 'casual'
  AND start_station_name IS NOT NULL
GROUP BY start_station_name
ORDER BY total_rides DESC
LIMIT 10;


-- ── 8. Top 10 stations d'arrivée — tous types ───────────────────────────────
SELECT
    member_casual,
    end_station_name,
    COUNT(*)                        AS total_rides
FROM cyclistic_clean
WHERE end_station_name IS NOT NULL
GROUP BY member_casual, end_station_name
ORDER BY member_casual, total_rides DESC
LIMIT 20;  -- 10 par type


-- ── 9. Répartition par heure de départ ──────────────────────────────────────
SELECT
    member_casual,
    hour_of_day,
    COUNT(*)                        AS total_rides,
    ROUND(AVG(ride_length), 2)      AS avg_ride_length_min
FROM cyclistic_clean
GROUP BY member_casual, hour_of_day
ORDER BY member_casual, hour_of_day;


-- ── 10. Jour de la semaine le plus populaire (mode) ─────────────────────────
-- Requête avec CTE pour trouver le mode par type d'utilisateur
WITH ranked_days AS (
    SELECT
        member_casual,
        day_of_week,
        COUNT(*)                    AS rides,
        ROW_NUMBER() OVER (
            PARTITION BY member_casual
            ORDER BY COUNT(*) DESC
        )                           AS rnk
    FROM cyclistic_clean
    GROUP BY member_casual, day_of_week
)
SELECT
    member_casual,
    day_of_week,
    CASE day_of_week
        WHEN 1 THEN 'Dimanche'
        WHEN 2 THEN 'Lundi'
        WHEN 3 THEN 'Mardi'
        WHEN 4 THEN 'Mercredi'
        WHEN 5 THEN 'Jeudi'
        WHEN 6 THEN 'Vendredi'
        WHEN 7 THEN 'Samedi'
    END                             AS most_popular_day,
    rides
FROM ranked_days
WHERE rnk = 1
ORDER BY member_casual;


-- ── 11. Comparaison membres vs casual — résumé pivot ────────────────────────
SELECT
    SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END)  AS member_rides,
    SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END)  AS casual_rides,
    ROUND(AVG(CASE WHEN member_casual = 'member' THEN ride_length END), 2)
                                                                AS member_avg_min,
    ROUND(AVG(CASE WHEN member_casual = 'casual' THEN ride_length END), 2)
                                                                AS casual_avg_min
FROM cyclistic_clean;


-- ── 12. Stations utilisées en commun (JOIN exemple) ─────────────────────────
-- Stations populaires pour LES DEUX types d'utilisateurs
WITH member_stations AS (
    SELECT start_station_name, COUNT(*) AS member_rides
    FROM cyclistic_clean
    WHERE member_casual = 'member' AND start_station_name IS NOT NULL
    GROUP BY start_station_name
),
casual_stations AS (
    SELECT start_station_name, COUNT(*) AS casual_rides
    FROM cyclistic_clean
    WHERE member_casual = 'casual' AND start_station_name IS NOT NULL
    GROUP BY start_station_name
)
SELECT
    m.start_station_name,
    m.member_rides,
    c.casual_rides,
    m.member_rides + c.casual_rides   AS total_rides
FROM member_stations m
JOIN casual_stations c USING (start_station_name)
ORDER BY total_rides DESC
LIMIT 20;
