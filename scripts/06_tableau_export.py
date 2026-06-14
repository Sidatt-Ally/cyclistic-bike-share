"""
06_tableau_export.py — Cyclistic Case Study
Prépare et exporte le CSV optimisé pour Tableau Desktop/Public.
À exécuter APRÈS 02_cleaning.py.
"""

import pandas as pd
import os

BASE_DIR = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
IN_CSV   = os.path.join(PROC_DIR, "cyclistic_clean.csv")
OUT_CSV  = os.path.join(PROC_DIR, "cyclistic_tableau.csv")

print("Chargement...")
df = pd.read_csv(IN_CSV, low_memory=False)
df["started_at"] = pd.to_datetime(df["started_at"])
df["ended_at"]   = pd.to_datetime(df["ended_at"])

# ── Colonnes supplémentaires utiles pour Tableau ──────────────────────────────
DOW_NAMES = {1:"Sunday",2:"Monday",3:"Tuesday",4:"Wednesday",
             5:"Thursday",6:"Friday",7:"Saturday"}
MONTH_NAMES = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
               7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

df["day_name"]        = df["day_of_week"].map(DOW_NAMES)
df["month_name"]      = df["month"].map(MONTH_NAMES)
df["is_weekend"]      = df["day_of_week"].isin([1, 7]).astype(int)
df["ride_length_hms"] = pd.to_datetime(df["ride_length"] * 60, unit="s").dt.strftime("%H:%M:%S")
df["member_label"]    = df["member_casual"].map({"member":"Member","casual":"Casual"})
df["start_date"]      = df["started_at"].dt.date.astype(str)
df["start_hour"]      = df["started_at"].dt.hour

# Ordre logique des colonnes pour Tableau
COLS_TABLEAU = [
    "ride_id",
    "member_casual", "member_label",
    "rideable_type",
    "started_at", "ended_at", "start_date",
    "ride_length", "ride_length_hms",
    "day_of_week", "day_name", "is_weekend",
    "month", "month_name", "year", "season",
    "start_hour", "hour_of_day",
    "start_station_name", "start_station_id",
    "end_station_name",   "end_station_id",
    "start_lat", "start_lng",
    "end_lat",   "end_lng",
]
# Garder seulement les colonnes existantes
cols = [c for c in COLS_TABLEAU if c in df.columns]
df_tableau = df[cols]

df_tableau.to_csv(OUT_CSV, index=False)
print(f"Export Tableau : {OUT_CSV}")
print(f"Lignes : {len(df_tableau):,} | Colonnes : {len(cols)}")
print("\nColonnes exportées :")
for c in cols:
    print(f"  - {c}")
