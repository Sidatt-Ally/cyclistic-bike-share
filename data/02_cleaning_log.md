# 02 - Cleaning Log

Run: 2026-06-14

## Etape 1 - Chargement des fichiers

- 202004-divvy-tripdata.csv: 84,776 lignes (schema standard 2020+)
- 202005-divvy-tripdata.csv: 200,274 lignes (schema standard 2020+)
- 202006-divvy-tripdata.csv: 343,005 lignes (schema standard 2020+)
- 202007-divvy-tripdata.csv: 551,480 lignes (schema standard 2020+)
- 202008-divvy-tripdata.csv: 622,361 lignes (schema standard 2020+)
- 202009-divvy-tripdata.csv: 532,958 lignes (schema standard 2020+)
- 202010-divvy-tripdata.csv: 388,653 lignes (schema standard 2020+)
- 202011-divvy-tripdata.csv: 259,716 lignes (schema standard 2020+)
- 202012-divvy-tripdata.csv: 131,573 lignes (schema standard 2020+)
- Divvy_Trips_2019_Q1.csv: 365,069 lignes (schema Legacy 2019, mapping applique)
- Divvy_Trips_2020_Q1.csv: 426,887 lignes (schema standard 2020+)

**Total brut : 3,906,752 lignes**

## Etape 2 - Conversion des colonnes datetime

- Dates non parsables supprimees : 0

## Etape 3 - Creation des colonnes derivees

- ride_length (minutes), day_of_week (1=Dim...7=Sam), month, year, hour_of_day, season crees

## Etape 4 - Suppression des doublons

- Doublons supprimes (sur ride_id) : 209

## Etape 5 - Suppression des rides invalides

- ride_length <= 0 supprimes : 10,917
- ride_length > 24h supprimes : 3,048
- Trajets de maintenance supprimes (HQ QR / TEST / DIVVY) : 7,139

## Etape 6 - Normalisation de member_casual

- Valeurs OK : uniquement 'member' et 'casual'

## Resume final

- Lignes avant nettoyage : 3,906,752
- Lignes apres nettoyage  : 3,885,439
- Supprimees au total     : 21,313 (0.5%)

### Distribution member_casual

- member : 2,508,757 (64.6%)
- casual : 1,376,682 (35.4%)

### Valeurs nulles restantes

- start_station_name : 94,565 nulls (2.4%)
- start_station_id   : 95,188 nulls (2.4%)
- end_station_name   : 110,046 nulls (2.8%)
- end_station_id     : 110,505 nulls (2.8%)
- start_lat / start_lng : 364,856 nulls (9.4%) -- trajets legacy 2019 Q1
- end_lat / end_lng     : 368,538 nulls (9.5%) -- trajets legacy 2019 Q1

Note : les nulls lat/lng proviennent du fichier Divvy_Trips_2019_Q1 
(schema legacy sans coordonnees GPS).

## Export

- Fichier : data/processed/cyclistic_clean.csv
- Export termine OK
