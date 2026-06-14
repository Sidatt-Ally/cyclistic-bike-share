"""
03_analysis.py — Cyclistic Case Study
Analyse descriptive et comparative members vs casual riders.
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
IN_CSV   = os.path.join(PROC_DIR, "cyclistic_clean.csv")
OUT_CSV  = os.path.join(PROC_DIR, "analysis_results.csv")

print("Chargement des données...")
df = pd.read_csv(IN_CSV, low_memory=False)
df["started_at"] = pd.to_datetime(df["started_at"])
print(f"  {len(df):,} lignes chargées\n")

results = {}

# ── 1. Statistiques descriptives globales ──────────────────────────────────────
print("1. Statistiques descriptives globales")
desc = df.groupby("member_casual")["ride_length"].agg(
    mean_ride_length="mean",
    median_ride_length="median",
    max_ride_length="max",
    min_ride_length="min",
    std_ride_length="std",
    total_rides="count"
).round(2).reset_index()
results["descriptive_stats"] = desc
print(desc.to_string(index=False))

# ── 2. Trajets par jour de la semaine ─────────────────────────────────────────
print("\n2. Trajets par jour de la semaine")
DOW_NAMES = {1:"Dimanche", 2:"Lundi", 3:"Mardi", 4:"Mercredi",
             5:"Jeudi", 6:"Vendredi", 7:"Samedi"}
dow = (df.groupby(["member_casual","day_of_week"])
         .agg(total_rides=("ride_id","count"),
              avg_ride_length=("ride_length","mean"))
         .round(2).reset_index())
dow["day_name"] = dow["day_of_week"].map(DOW_NAMES)
results["rides_by_dow"] = dow
print(dow.pivot(index="day_name", columns="member_casual", values="total_rides"))

# ── 3. Trajets par mois ────────────────────────────────────────────────────────
print("\n3. Trajets par mois")
MONTH_NAMES = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Juin",
               7:"Juil",8:"Août",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}
monthly = (df.groupby(["member_casual","year","month"])
             .agg(total_rides=("ride_id","count"),
                  avg_ride_length=("ride_length","mean"))
             .round(2).reset_index())
monthly["month_name"] = monthly["month"].map(MONTH_NAMES)
results["rides_by_month"] = monthly
print(monthly.pivot_table(index=["year","month"], columns="member_casual",
                           values="total_rides", aggfunc="sum"))

# ── 4. Trajets par saison ──────────────────────────────────────────────────────
print("\n4. Trajets par saison")
seasonal = (df.groupby(["member_casual","season"])
              .agg(total_rides=("ride_id","count"),
                   avg_ride_length=("ride_length","mean"))
              .round(2).reset_index())
results["rides_by_season"] = seasonal
print(seasonal.pivot(index="season", columns="member_casual", values="total_rides"))

# ── 5. Types de vélos ──────────────────────────────────────────────────────────
print("\n5. Types de vélos")
bike_types = (df.groupby(["member_casual","rideable_type"])
                .agg(total_rides=("ride_id","count"),
                     avg_ride_length=("ride_length","mean"))
                .round(2).reset_index())
bike_types["pct"] = (bike_types["total_rides"] /
                     bike_types.groupby("member_casual")["total_rides"].transform("sum") * 100).round(1)
results["bike_types"] = bike_types
print(bike_types.pivot(index="rideable_type", columns="member_casual", values="total_rides"))

# ── 6. Top 10 stations départ ──────────────────────────────────────────────────
print("\n6. Top 10 stations de départ")
start_stations = (df[df["start_station_name"].notna()]
                  .groupby(["member_casual","start_station_name"])
                  .size().reset_index(name="total_rides")
                  .sort_values(["member_casual","total_rides"], ascending=[True, False]))
top10_start = start_stations.groupby("member_casual").head(10).reset_index(drop=True)
results["top10_start_stations"] = top10_start

# ── 7. Top 10 stations arrivée ────────────────────────────────────────────────
end_stations = (df[df["end_station_name"].notna()]
                .groupby(["member_casual","end_station_name"])
                .size().reset_index(name="total_rides")
                .sort_values(["member_casual","total_rides"], ascending=[True, False]))
top10_end = end_stations.groupby("member_casual").head(10).reset_index(drop=True)
results["top10_end_stations"] = top10_end

# ── 8. Trajets par heure ───────────────────────────────────────────────────────
print("\n8. Trajets par heure de la journée")
hourly = (df.groupby(["member_casual","hour_of_day"])
            .agg(total_rides=("ride_id","count"))
            .reset_index())
results["rides_by_hour"] = hourly

# ── 9. Mode (jour le plus populaire) ──────────────────────────────────────────
print("\n9. Jour le plus populaire par type d'utilisateur")
for user_type in ["member", "casual"]:
    subset = df[df["member_casual"] == user_type]
    mode_dow = subset["day_of_week"].mode()[0]
    print(f"  {user_type}: {DOW_NAMES[mode_dow]} (code {mode_dow})")

# ── Export ─────────────────────────────────────────────────────────────────────
print(f"\nExport de tous les résultats vers {OUT_CSV}")
with pd.ExcelWriter(OUT_CSV.replace(".csv", ".xlsx"), engine="openpyxl") as writer:
    for sheet_name, df_res in results.items():
        df_res.to_excel(writer, sheet_name=sheet_name[:31], index=False)

# Export CSV consolidé (descriptive stats + monthly comme référence principale)
main_export = pd.concat([
    desc.assign(analysis="descriptive_stats"),
], ignore_index=True)
desc.to_csv(OUT_CSV, index=False)
print("  Export terminé ✓")

# Afficher résumé
print("\n" + "="*60)
print("RÉSUMÉ CLÉS")
print("="*60)
for _, row in desc.iterrows():
    print(f"\n{row['member_casual'].upper()}")
    print(f"  Trajets totaux    : {int(row['total_rides']):,}")
    print(f"  Durée moyenne     : {row['mean_ride_length']:.1f} min")
    print(f"  Durée médiane     : {row['median_ride_length']:.1f} min")
    print(f"  Durée max         : {row['max_ride_length']:.1f} min")
