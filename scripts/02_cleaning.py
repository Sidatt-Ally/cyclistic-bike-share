"""
02_cleaning.py — Cyclistic Case Study
Nettoyage et consolidation de tous les fichiers de données Divvy.
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

# ── Chemins ────────────────────────────────────────────────────────────────────
BASE_DIR   = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
LOG_PATH   = os.path.join(BASE_DIR, "data", "02_cleaning_log.md")
OUT_CSV    = os.path.join(PROC_DIR, "cyclistic_clean.csv")

os.makedirs(PROC_DIR, exist_ok=True)

log_lines = ["# 02 — Cleaning Log\n", f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"]

def log(msg):
    print(msg)
    log_lines.append(msg + "\n")

# ── Schéma 2020+ ───────────────────────────────────────────────────────────────
COLS_2020 = [
    "ride_id", "rideable_type", "started_at", "ended_at",
    "start_station_name", "start_station_id",
    "end_station_name",   "end_station_id",
    "start_lat", "start_lng", "end_lat", "end_lng",
    "member_casual"
]

# ── Mapping schéma Legacy 2019 ──────────────────────────────────────────────────
def load_legacy_2019(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df = df.rename(columns={
        "trip_id":          "ride_id",
        "start_time":       "started_at",
        "end_time":         "ended_at",
        "from_station_id":  "start_station_id",
        "from_station_name":"start_station_name",
        "to_station_id":    "end_station_id",
        "to_station_name":  "end_station_name",
        "usertype":         "member_casual",
    })
    # Subscriber → member, Customer → casual
    df["member_casual"] = df["member_casual"].replace({
        "Subscriber": "member",
        "Customer":   "casual"
    })
    df["rideable_type"] = "unknown"
    df["start_lat"] = np.nan
    df["start_lng"] = np.nan
    df["end_lat"]   = np.nan
    df["end_lng"]   = np.nan
    return df[COLS_2020]

# ── Chargement ─────────────────────────────────────────────────────────────────
log("## Étape 1 — Chargement des fichiers\n")
all_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
frames = []
total_raw = 0

for fp in all_files:
    fname = os.path.basename(fp)
    if "2019_Q1" in fname:
        df = load_legacy_2019(fp)
        log(f"- {fname}: {len(df):,} lignes (schéma Legacy 2019, mapping appliqué)")
    else:
        df = pd.read_csv(fp, low_memory=False)
        log(f"- {fname}: {len(df):,} lignes (schéma standard 2020+)")
    total_raw += len(df)
    frames.append(df)

df = pd.concat(frames, ignore_index=True)
log(f"\n**Total brut : {total_raw:,} lignes**\n")

# ── Colonnes datetime ──────────────────────────────────────────────────────────
log("## Étape 2 — Conversion des colonnes datetime\n")
df["started_at"] = pd.to_datetime(df["started_at"], infer_datetime_format=True, errors="coerce")
df["ended_at"]   = pd.to_datetime(df["ended_at"],   infer_datetime_format=True, errors="coerce")
nat_count = df["started_at"].isna().sum() + df["ended_at"].isna().sum()
log(f"- Dates non parsables supprimées : {nat_count:,}")
df = df.dropna(subset=["started_at", "ended_at"])

# ── Colonnes calculées ─────────────────────────────────────────────────────────
log("\n## Étape 3 — Création des colonnes dérivées\n")
df["ride_length"]  = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
df["day_of_week"]  = df["started_at"].dt.dayofweek.map(
    {6:1, 0:2, 1:3, 2:4, 3:5, 4:6, 5:7}  # 1=Dim, 7=Sam
)
df["month"]        = df["started_at"].dt.month
df["year"]         = df["started_at"].dt.year
df["hour_of_day"]  = df["started_at"].dt.hour
df["season"]       = df["month"].map({
    12:"Winter", 1:"Winter", 2:"Winter",
    3:"Spring",  4:"Spring", 5:"Spring",
    6:"Summer",  7:"Summer", 8:"Summer",
    9:"Fall",   10:"Fall",  11:"Fall"
})
log("- ride_length (minutes), day_of_week (1=Dim…7=Sam), month, year, hour_of_day, season créés")

# ── Suppression des doublons ───────────────────────────────────────────────────
log("\n## Étape 4 — Suppression des doublons\n")
before = len(df)
df = df.drop_duplicates(subset=["ride_id"])
removed_dup = before - len(df)
log(f"- Doublons supprimés : {removed_dup:,}")

# ── Rides invalides ────────────────────────────────────────────────────────────
log("\n## Étape 5 — Suppression des rides invalides\n")

# ride_length <= 0
before = len(df)
df = df[df["ride_length"] > 0]
log(f"- ride_length <= 0 supprimés : {before - len(df):,}")

# ride_length > 1440 minutes (24h) → vélos non retournés
before = len(df)
df = df[df["ride_length"] <= 1440]
log(f"- ride_length > 24h supprimés : {before - len(df):,}")

# Trajets de maintenance (station HQ)
before = len(df)
mask_hq = (
    df["start_station_name"].str.contains("HQ QR|DIVVY|TEST|Hubbard Bike-checking",
                                           case=False, na=False) |
    df["end_station_name"].str.contains("HQ QR|DIVVY|TEST|Hubbard Bike-checking",
                                         case=False, na=False)
)
df = df[~mask_hq]
log(f"- Trajets de maintenance supprimés : {before - len(df):,}")

# ── Normalisation member_casual ────────────────────────────────────────────────
log("\n## Étape 6 — Normalisation de member_casual\n")
df["member_casual"] = df["member_casual"].str.strip().str.lower()
invalid_types = df[~df["member_casual"].isin(["member","casual"])]["member_casual"].unique()
if len(invalid_types) > 0:
    log(f"- Valeurs inconnues trouvées et supprimées : {invalid_types}")
    df = df[df["member_casual"].isin(["member","casual"])]
else:
    log("- Valeurs OK : uniquement 'member' et 'casual'")

# ── Résumé final ───────────────────────────────────────────────────────────────
log(f"\n## Résumé final\n")
log(f"- Lignes avant nettoyage : {total_raw:,}")
log(f"- Lignes après nettoyage : {len(df):,}")
log(f"- Supprimées au total    : {total_raw - len(df):,} ({(total_raw - len(df))/total_raw*100:.1f}%)")
log(f"\n### Distribution member_casual\n")
for k, v in df["member_casual"].value_counts().items():
    log(f"- {k}: {v:,} ({v/len(df)*100:.1f}%)")
log(f"\n### Valeurs nulles restantes\n")
nulls = df.isnull().sum()
for col, n in nulls[nulls > 0].items():
    log(f"- {col}: {n:,} nulls ({n/len(df)*100:.1f}%)")

# ── Export ─────────────────────────────────────────────────────────────────────
log(f"\n## Export\n- Fichier : {OUT_CSV}")
df.to_csv(OUT_CSV, index=False)
log(f"- Export termine OK")

# Écriture du log
with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print(f"\nLog écrit dans : {LOG_PATH}")
print(f"CSV propre : {OUT_CSV}")
