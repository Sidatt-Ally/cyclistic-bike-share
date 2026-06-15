"""
04_load_postgres.py — Chargement des données Cyclistic dans PostgreSQL
Tables créées :
  - cyclistic_raw      : 11 CSV bruts concaténés (pour pratiquer le nettoyage SQL)
  - cyclistic_clean    : données nettoyées (pour pratiquer l'analyse SQL)
  - cyclistic_tableau  : données enrichies avec colonnes Tableau

Connexion : localhost:5432 / user=postgres / db=cyclistic_db
"""

import os
import time
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ── Paramètres de connexion ───────────────────────────────────────────────────
DB_PARAMS = {
    "host":     "localhost",
    "port":     5432,
    "user":     "postgres",
    "password": "postgres",
}
DB_NAME   = "cyclistic_db"
BASE_DIR  = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
RAW_DIR   = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR  = os.path.join(BASE_DIR, "data", "processed")

# Fichiers bruts (ordre chronologique)
RAW_FILES = [
    "Divvy_Trips_2019_Q1.csv",
    "Divvy_Trips_2020_Q1.csv",
    "202004-divvy-tripdata.csv",
    "202005-divvy-tripdata.csv",
    "202006-divvy-tripdata.csv",
    "202007-divvy-tripdata.csv",
    "202008-divvy-tripdata.csv",
    "202009-divvy-tripdata.csv",
    "202010-divvy-tripdata.csv",
    "202011-divvy-tripdata.csv",
    "202012-divvy-tripdata.csv",
]

# ── Schémas SQL ───────────────────────────────────────────────────────────────

# Table brute : colonnes du format 2020 (schéma unifié après renommage)
DDL_RAW = """
CREATE TABLE IF NOT EXISTS cyclistic_raw (
    ride_id             TEXT,
    rideable_type       TEXT,
    started_at          TEXT,       -- brut : TEXT pour pratiquer la conversion
    ended_at            TEXT,       -- brut : TEXT pour pratiquer la conversion
    start_station_name  TEXT,
    start_station_id    TEXT,
    end_station_name    TEXT,
    end_station_id      TEXT,
    start_lat           TEXT,
    start_lng           TEXT,
    end_lat             TEXT,
    end_lng             TEXT,
    member_casual       TEXT,
    source_file         TEXT        -- colonne ajoutée pour tracer l'origine
);
"""

# Table nettoyée : types corrects + colonnes calculées
DDL_CLEAN = """
CREATE TABLE IF NOT EXISTS cyclistic_clean (
    ride_id             TEXT,
    rideable_type       TEXT,
    started_at          TIMESTAMP,
    ended_at            TIMESTAMP,
    ride_length         NUMERIC(10,2),
    day_of_week         SMALLINT,
    month               SMALLINT,
    year                SMALLINT,
    hour_of_day         SMALLINT,
    season              TEXT,
    start_station_name  TEXT,
    start_station_id    TEXT,
    end_station_name    TEXT,
    end_station_id      TEXT,
    start_lat           NUMERIC(10,6),
    start_lng           NUMERIC(10,6),
    end_lat             NUMERIC(10,6),
    end_lng             NUMERIC(10,6),
    member_casual       TEXT
);
"""

# Table Tableau : colonnes enrichies
DDL_TABLEAU = """
CREATE TABLE IF NOT EXISTS cyclistic_tableau (
    ride_id             TEXT,
    member_casual       TEXT,
    member_label        TEXT,
    rideable_type       TEXT,
    started_at          TIMESTAMP,
    ended_at            TIMESTAMP,
    start_date          DATE,
    ride_length         NUMERIC(10,2),
    ride_length_hms     TEXT,
    day_of_week         SMALLINT,
    day_name            TEXT,
    is_weekend          SMALLINT,
    month               SMALLINT,
    month_name          TEXT,
    year                SMALLINT,
    season              TEXT,
    start_hour          SMALLINT,
    hour_of_day         SMALLINT,
    start_station_name  TEXT,
    start_station_id    TEXT,
    end_station_name    TEXT,
    end_station_id      TEXT,
    start_lat           NUMERIC(10,6),
    start_lng           NUMERIC(10,6),
    end_lat             NUMERIC(10,6),
    end_lng             NUMERIC(10,6)
);
"""

# ── Colonnes legacy 2019 → colonnes 2020 ─────────────────────────────────────
LEGACY_2019_RENAME = {
    "trip_id":            "ride_id",
    "start_time":         "started_at",
    "end_time":           "ended_at",
    "from_station_id":    "start_station_id",
    "from_station_name":  "start_station_name",
    "to_station_id":      "end_station_id",
    "to_station_name":    "end_station_name",
    "usertype":           "member_casual",
}
USERTYPE_MAP = {"Subscriber": "member", "Customer": "casual"}

# Colonnes attendues dans cyclistic_raw (dans l'ordre du DDL)
RAW_COLS = [
    "ride_id", "rideable_type", "started_at", "ended_at",
    "start_station_name", "start_station_id",
    "end_station_name", "end_station_id",
    "start_lat", "start_lng", "end_lat", "end_lng",
    "member_casual",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def banner(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)

def log(msg):
    print(f"  >> {msg}")

def create_database(params, dbname):
    """Crée la base de données si elle n'existe pas."""
    conn = psycopg2.connect(**params, database="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
        log(f"Base '{dbname}' créée.")
    else:
        log(f"Base '{dbname}' existe déjà.")
    cur.close()
    conn.close()

def get_conn():
    return psycopg2.connect(**DB_PARAMS, database=DB_NAME)

def copy_csv(cur, filepath, table, columns):
    """Charge un CSV dans une table via COPY (très rapide)."""
    # Remplace les backslashes Windows par des slashes pour PostgreSQL
    pg_path = filepath.replace("\\", "/")
    col_list = ", ".join(columns)
    query = f"""
        COPY {table} ({col_list})
        FROM '{pg_path}'
        WITH (
            FORMAT csv,
            HEADER true,
            NULL '',
            ENCODING 'UTF8'
        );
    """
    cur.execute(query)

# ── Chargement cyclistic_raw ─────────────────────────────────────────────────
def load_raw(conn):
    banner("CHARGEMENT cyclistic_raw (données brutes)")
    cur = conn.cursor()

    # Vider la table si elle existe déjà
    cur.execute("TRUNCATE TABLE cyclistic_raw;")
    log("Table vidée (TRUNCATE).")

    total = 0
    for fname in RAW_FILES:
        fpath = os.path.join(RAW_DIR, fname)
        if not os.path.exists(fpath):
            log(f"[IGNORÉ] Fichier introuvable : {fname}")
            continue

        t0 = time.time()
        is_legacy = "2019" in fname

        if is_legacy:
            # Le fichier 2019 a un schéma différent → on passe par un fichier temporaire
            import pandas as pd, tempfile
            df = pd.read_csv(fpath, low_memory=False)
            df = df.rename(columns=LEGACY_2019_RENAME)
            df["member_casual"] = df["member_casual"].replace(USERTYPE_MAP)
            df["rideable_type"] = "unknown"
            # Garder uniquement les colonnes RAW_COLS qui existent
            for c in RAW_COLS:
                if c not in df.columns:
                    df[c] = ""
            df = df[RAW_COLS]
            df["source_file"] = fname

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False,
                encoding="utf-8", newline=""
            ) as tmp:
                df.to_csv(tmp, index=False)
                tmp_path = tmp.name

            with open(tmp_path, encoding="utf-8") as f:
                cur.copy_expert(
                    f"COPY cyclistic_raw ({', '.join(RAW_COLS + ['source_file'])}) "
                    f"FROM STDIN WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8')",
                    f
                )
            os.unlink(tmp_path)
        else:
            # Fichiers 2020 : COPY direct avec colonne source_file
            # On doit ajouter source_file via INSERT SELECT depuis une table temp
            import pandas as pd, tempfile
            df = pd.read_csv(fpath, low_memory=False)
            for c in RAW_COLS:
                if c not in df.columns:
                    df[c] = ""
            df = df[RAW_COLS]
            df["source_file"] = fname

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False,
                encoding="utf-8", newline=""
            ) as tmp:
                df.to_csv(tmp, index=False)
                tmp_path = tmp.name

            with open(tmp_path, encoding="utf-8") as f:
                cur.copy_expert(
                    f"COPY cyclistic_raw ({', '.join(RAW_COLS + ['source_file'])}) "
                    f"FROM STDIN WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8')",
                    f
                )
            os.unlink(tmp_path)

        cur.execute("SELECT COUNT(*) FROM cyclistic_raw")
        current = cur.fetchone()[0]
        rows_added = current - total
        total = current
        elapsed = time.time() - t0
        log(f"{fname:<45} +{rows_added:>8,} lignes  ({elapsed:.1f}s)")

    conn.commit()
    cur.close()
    log(f"\nTOTAL cyclistic_raw : {total:,} lignes")

# ── Chargement cyclistic_clean ───────────────────────────────────────────────
def load_clean(conn):
    banner("CHARGEMENT cyclistic_clean (données nettoyées)")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE cyclistic_clean;")
    log("Table vidée.")

    fpath = os.path.join(PROC_DIR, "cyclistic_clean.csv")
    if not os.path.exists(fpath):
        log(f"[ERREUR] Fichier introuvable : {fpath}")
        log("Exécute d'abord : python scripts/02_cleaning.py")
        cur.close()
        return

    t0 = time.time()
    import pandas as pd, tempfile
    log("Lecture du CSV nettoyé...")
    df = pd.read_csv(fpath, low_memory=False)

    # Colonnes attendues dans cyclistic_clean
    clean_cols = [
        "ride_id", "rideable_type", "started_at", "ended_at",
        "ride_length", "day_of_week", "month", "year", "hour_of_day", "season",
        "start_station_name", "start_station_id",
        "end_station_name", "end_station_id",
        "start_lat", "start_lng", "end_lat", "end_lng",
        "member_casual",
    ]
    for c in clean_cols:
        if c not in df.columns:
            df[c] = None
    df = df[clean_cols]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False,
        encoding="utf-8", newline=""
    ) as tmp:
        df.to_csv(tmp, index=False)
        tmp_path = tmp.name

    log("Chargement COPY en cours...")
    with open(tmp_path, encoding="utf-8") as f:
        cur.copy_expert(
            f"COPY cyclistic_clean ({', '.join(clean_cols)}) "
            f"FROM STDIN WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8')",
            f
        )
    os.unlink(tmp_path)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM cyclistic_clean")
    n = cur.fetchone()[0]
    elapsed = time.time() - t0
    cur.close()
    log(f"TOTAL cyclistic_clean : {n:,} lignes  ({elapsed:.1f}s)")

# ── Chargement cyclistic_tableau ─────────────────────────────────────────────
def load_tableau(conn):
    banner("CHARGEMENT cyclistic_tableau (données enrichies Tableau)")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE cyclistic_tableau;")
    log("Table vidée.")

    fpath = os.path.join(PROC_DIR, "cyclistic_tableau.csv")
    if not os.path.exists(fpath):
        log(f"[ERREUR] Fichier introuvable : {fpath}")
        log("Exécute d'abord : python scripts/06_tableau_export.py")
        cur.close()
        return

    t0 = time.time()
    import pandas as pd, tempfile
    log("Lecture du CSV Tableau...")
    df = pd.read_csv(fpath, low_memory=False)

    tableau_cols = [
        "ride_id", "member_casual", "member_label", "rideable_type",
        "started_at", "ended_at", "start_date",
        "ride_length", "ride_length_hms",
        "day_of_week", "day_name", "is_weekend",
        "month", "month_name", "year", "season",
        "start_hour", "hour_of_day",
        "start_station_name", "start_station_id",
        "end_station_name", "end_station_id",
        "start_lat", "start_lng", "end_lat", "end_lng",
    ]
    cols_present = [c for c in tableau_cols if c in df.columns]
    df = df[cols_present]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False,
        encoding="utf-8", newline=""
    ) as tmp:
        df.to_csv(tmp, index=False)
        tmp_path = tmp.name

    log("Chargement COPY en cours...")
    with open(tmp_path, encoding="utf-8") as f:
        cur.copy_expert(
            f"COPY cyclistic_tableau ({', '.join(cols_present)}) "
            f"FROM STDIN WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8')",
            f
        )
    os.unlink(tmp_path)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM cyclistic_tableau")
    n = cur.fetchone()[0]
    elapsed = time.time() - t0
    cur.close()
    log(f"TOTAL cyclistic_tableau : {n:,} lignes  ({elapsed:.1f}s)")

# ── Validation finale ────────────────────────────────────────────────────────
def validate(conn):
    banner("VALIDATION")
    cur = conn.cursor()
    tables = ["cyclistic_raw", "cyclistic_clean", "cyclistic_tableau"]
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position", (t,)
        )
        cols = [r[0] for r in cur.fetchall()]
        log(f"{t:<25} {n:>10,} lignes  |  {len(cols)} colonnes")
    cur.close()

    print("\n  Connexion psycopg2 pour Python :")
    print(f'  conn = psycopg2.connect(host="localhost", port=5432,')
    print(f'                          dbname="cyclistic_db",')
    print(f'                          user="postgres", password="postgres")')
    print("\n  Tables disponibles :")
    print("    • cyclistic_raw     → pratiquer le nettoyage SQL / Python")
    print("    • cyclistic_clean   → pratiquer les requêtes d'analyse")
    print("    • cyclistic_tableau → colonnes enrichies (day_name, season…)")

# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nCyclistic PostgreSQL Loader")
    print("Connexion : postgresql://postgres@localhost:5432/cyclistic_db\n")

    # 1. Créer la base
    banner("CRÉATION DE LA BASE cyclistic_db")
    create_database(DB_PARAMS, DB_NAME)

    # 2. Créer les tables
    conn = get_conn()
    cur = conn.cursor()
    banner("CRÉATION DES TABLES")
    for name, ddl in [
        ("cyclistic_raw",     DDL_RAW),
        ("cyclistic_clean",   DDL_CLEAN),
        ("cyclistic_tableau", DDL_TABLEAU),
    ]:
        cur.execute(ddl)
        log(f"Table '{name}' prête.")
    conn.commit()
    cur.close()

    # 3. Charger les données
    load_raw(conn)
    load_clean(conn)
    load_tableau(conn)

    # 4. Valider
    validate(conn)
    conn.close()

    print("\nOK - Chargement termine. Base 'cyclistic_db' prete pour la pratique SQL & Python.")
