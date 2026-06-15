"""
04_visualizations.py — Cyclistic Case Study
Génération de tous les graphiques avec matplotlib/seaborn.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

BASE_DIR   = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
FIG_DIR    = os.path.join(BASE_DIR, "figures")
IN_CSV     = os.path.join(PROC_DIR, "cyclistic_clean.csv")
os.makedirs(FIG_DIR, exist_ok=True)

# ── Palette & style ────────────────────────────────────────────────────────────
PALETTE    = {"member": "#1A73E8", "casual": "#34A853"}   # bleu / vert Cyclistic
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "font.family":      "DejaVu Sans",
})

DOW_NAMES  = {1:"Dim", 2:"Lun", 3:"Mar", 4:"Mer", 5:"Jeu", 6:"Ven", 7:"Sam"}
MONTH_NAMES = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jui",
               7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}
SEASON_ORDER = ["Spring","Summer","Fall","Winter"]

print("Chargement des données...")
df = pd.read_csv(IN_CSV, low_memory=False)
print(f"  {len(df):,} lignes\n")


def save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Sauvegardé : {name}")


# ── Fig 1 — Nombre de trajets : membres vs casual ─────────────────────────────
print("Fig 1 — Nombre de trajets")
counts = df["member_casual"].value_counts().reset_index()
counts.columns = ["member_casual", "total_rides"]
counts["label"] = counts["total_rides"].apply(lambda x: f"{x/1e6:.2f}M")

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(counts["member_casual"], counts["total_rides"],
              color=[PALETTE[t] for t in counts["member_casual"]], width=0.5, edgecolor="white")
for bar, lbl in zip(bars, counts["label"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20000,
            lbl, ha="center", va="bottom", fontsize=13, fontweight="bold")
ax.set_title("Nombre total de trajets\nMembres vs Casual", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Type d'utilisateur", fontsize=12)
ax.set_ylabel("Nombre de trajets", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.set_ylim(0, counts["total_rides"].max() * 1.15)
ax.tick_params(axis="x", labelsize=13)
fig.tight_layout()
save(fig, "01_rides_count.png")


# ── Fig 2 — Durée moyenne des trajets ────────────────────────────────────────
print("Fig 2 — Durée moyenne")
avg_len = df.groupby("member_casual")["ride_length"].mean().reset_index()
avg_len.columns = ["member_casual", "avg_min"]

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(avg_len["member_casual"], avg_len["avg_min"],
              color=[PALETTE[t] for t in avg_len["member_casual"]], width=0.5, edgecolor="white")
for bar, row in zip(bars, avg_len.itertuples()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{row.avg_min:.1f} min", ha="center", va="bottom", fontsize=13, fontweight="bold")
ax.set_title("Durée moyenne des trajets\nMembres vs Casual", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Type d'utilisateur", fontsize=12)
ax.set_ylabel("Durée moyenne (minutes)", fontsize=12)
ax.set_ylim(0, avg_len["avg_min"].max() * 1.2)
ax.tick_params(axis="x", labelsize=13)
fig.tight_layout()
save(fig, "02_avg_ride_length.png")


# ── Fig 3 — Trajets par jour de la semaine ────────────────────────────────────
print("Fig 3 — Trajets par jour")
dow = (df.groupby(["day_of_week","member_casual"])
         .size().reset_index(name="total_rides"))
dow["day_name"] = dow["day_of_week"].map(DOW_NAMES)
dow_order = [DOW_NAMES[i] for i in range(1, 8)]

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=dow, x="day_name", y="total_rides", hue="member_casual",
            order=dow_order, palette=PALETTE, ax=ax, edgecolor="white")
ax.set_title("Trajets par jour de la semaine\nMembres vs Casual", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Jour de la semaine", fontsize=12)
ax.set_ylabel("Nombre de trajets", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
ax.legend(title="Type", fontsize=11, title_fontsize=11)
fig.tight_layout()
save(fig, "03_rides_by_dow.png")


# ── Fig 4 — Trajets par mois (line chart) ────────────────────────────────────
print("Fig 4 — Trajets par mois")
monthly = (df.groupby(["year","month","member_casual"])
             .size().reset_index(name="total_rides"))
monthly["month_name"] = monthly["month"].map(MONTH_NAMES)
monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
monthly = monthly.sort_values("period")

fig, ax = plt.subplots(figsize=(14, 6))
for user_type, grp in monthly.groupby("member_casual"):
    ax.plot(grp["period"], grp["total_rides"], marker="o", linewidth=2.5,
            label=user_type.capitalize(), color=PALETTE[user_type])
    for _, row in grp.iterrows():
        if row["total_rides"] > 100000:
            ax.annotate(f"{row['total_rides']/1000:.0f}k",
                        (row["period"], row["total_rides"]),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=8, color=PALETTE[user_type])
ax.set_title("Nombre de trajets par mois\nMembres vs Casual", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Période", fontsize=12)
ax.set_ylabel("Nombre de trajets", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
plt.xticks(rotation=45, ha="right", fontsize=9)
ax.legend(title="Type", fontsize=11)
fig.tight_layout()
save(fig, "04_rides_by_month.png")


# ── Fig 5 — Types de vélos ────────────────────────────────────────────────────
print("Fig 5 — Types de vélos")
bikes = (df.groupby(["member_casual","rideable_type"])
           .size().reset_index(name="total_rides"))
bikes = bikes[bikes["rideable_type"] != "unknown"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
# Palette alignée sur le dashboard : orange / violet / or (distinct de bleu membre et vert casual)
bike_palette = ["#FF8C42", "#6C63FF", "#F7C948"]
for ax, user_type in zip(axes, ["member","casual"]):
    subset = bikes[bikes["member_casual"] == user_type].reset_index(drop=True)
    wedges, texts, autotexts = ax.pie(
        subset["total_rides"],
        labels=None,
        autopct="%1.1f%%",
        colors=bike_palette[:len(subset)],
        startangle=90,
        pctdistance=0.78,
        wedgeprops=dict(width=0.6, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
    ax.set_title(f"Types de vélos — {user_type.capitalize()}", fontsize=13, fontweight="bold")
    ax.legend(subset["rideable_type"], loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=9, frameon=False)
fig.suptitle("Types de vélos utilisés", fontsize=15, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "05_bike_types.png")


# ── Fig 6 — Top 10 stations casual (cibles marketing) ────────────────────────
print("Fig 6 — Top 10 stations casual")
top_casual = (df[(df["start_station_name"].notna()) & (df["member_casual"] == "casual")]
              .groupby("start_station_name")
              .size().reset_index(name="total_rides")
              .sort_values("total_rides", ascending=False)
              .head(10).reset_index(drop=True))

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(top_casual["start_station_name"], top_casual["total_rides"],
               color=PALETTE["casual"], edgecolor="white")
for bar, val in zip(bars, top_casual["total_rides"]):
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
            f"{val:,}", va="center", fontsize=10)
ax.set_title("Top 10 stations de départ — Casual riders\n(cibles prioritaires pour la conversion)",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Nombre de trajets casual", fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
ax.invert_yaxis()
fig.tight_layout()
save(fig, "06_top10_stations.png")


# ── Fig 7 — Trajets par heure ─────────────────────────────────────────────────
print("Fig 7 — Trajets par heure")
hourly = (df.groupby(["hour_of_day","member_casual"])
            .size().reset_index(name="total_rides"))

fig, ax = plt.subplots(figsize=(12, 5))
for user_type, grp in hourly.groupby("member_casual"):
    ax.plot(grp["hour_of_day"], grp["total_rides"], marker="o", linewidth=2.5,
            label=user_type.capitalize(), color=PALETTE[user_type])
ax.set_title("Répartition des trajets par heure de départ", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Heure de départ", fontsize=12)
ax.set_ylabel("Nombre de trajets", fontsize=12)
ax.set_xticks(range(0, 24))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}k"))
ax.axvspan(7, 9, alpha=0.1, color="orange", label="Rush matin")
ax.axvspan(16, 18, alpha=0.1, color="red", label="Rush soir")
ax.legend(fontsize=11)
fig.tight_layout()
save(fig, "07_rides_by_hour.png")


# ── Fig 8 — Durée moyenne par jour de la semaine ─────────────────────────────
print("Fig 8 — Durée par jour")
dow_len = (df.groupby(["day_of_week","member_casual"])["ride_length"]
             .mean().reset_index())
dow_len["day_name"] = dow_len["day_of_week"].map(DOW_NAMES)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=dow_len, x="day_name", y="ride_length", hue="member_casual",
            order=dow_order, palette=PALETTE, ax=ax, edgecolor="white")
ax.set_title("Durée moyenne des trajets par jour\nMembres vs Casual", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Jour de la semaine", fontsize=12)
ax.set_ylabel("Durée moyenne (minutes)", fontsize=12)
ax.legend(title="Type", fontsize=11)
fig.tight_layout()
save(fig, "08_avg_length_by_dow.png")

print("\nTous les graphiques ont été générés dans :", FIG_DIR)
