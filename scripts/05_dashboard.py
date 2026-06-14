"""
05_dashboard.py — Cyclistic Case Study
Génère le dashboard HTML interactif avec Plotly (standalone, ouvrable dans un navigateur).
À exécuter APRÈS 02_cleaning.py et 03_analysis.py.
"""

import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

BASE_DIR  = r"C:\Users\Republic Of Computer\Desktop\Cyclistic_Project"
PROC_DIR  = os.path.join(BASE_DIR, "data", "processed")
IN_CSV    = os.path.join(PROC_DIR, "cyclistic_clean.csv")
OUT_HTML  = os.path.join(BASE_DIR, "05_dashboard.html")

# ── Couleurs Cyclistic ─────────────────────────────────────────────────────────
COLOR_MEMBER = "#1A73E8"   # bleu
COLOR_CASUAL = "#34A853"   # vert
COLOR_MAP    = {"member": COLOR_MEMBER, "casual": COLOR_CASUAL}
BG_COLOR     = "#F8F9FA"
CARD_COLOR   = "#FFFFFF"

DOW_NAMES    = {1:"Dimanche", 2:"Lundi", 3:"Mardi", 4:"Mercredi",
                5:"Jeudi", 6:"Vendredi", 7:"Samedi"}
MONTH_NAMES  = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jui",
                7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}

print("Chargement des données...")
df = pd.read_csv(IN_CSV, low_memory=False)
df["started_at"] = pd.to_datetime(df["started_at"])
print(f"  {len(df):,} lignes chargées\n")

# ── Données agrégées ───────────────────────────────────────────────────────────
counts     = df["member_casual"].value_counts().reset_index()
counts.columns = ["member_casual", "total_rides"]

avg_len    = df.groupby("member_casual")["ride_length"].mean().reset_index()
avg_len.columns = ["member_casual", "avg_min"]

dow        = (df.groupby(["day_of_week","member_casual"])
               .agg(total_rides=("ride_id","count"),
                    avg_length=("ride_length","mean"))
               .reset_index())
dow["day_name"] = dow["day_of_week"].map(DOW_NAMES)
dow_order  = [DOW_NAMES[i] for i in range(1, 8)]

monthly    = (df.groupby(["year","month","member_casual"])
               .size().reset_index(name="total_rides"))
monthly["period"]     = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
monthly["month_name"] = monthly["month"].map(MONTH_NAMES)
monthly    = monthly.sort_values("period")

bikes      = (df[df["rideable_type"] != "unknown"]
              .groupby(["member_casual","rideable_type"])
              .size().reset_index(name="total_rides"))

top10_casual  = (df[(df["start_station_name"].notna()) & (df["member_casual"]=="casual")]
                 .groupby("start_station_name")
                 .size().reset_index(name="total_rides")
                 .sort_values("total_rides", ascending=False)
                 .head(10))

top10_member  = (df[(df["start_station_name"].notna()) & (df["member_casual"]=="member")]
                 .groupby("start_station_name")
                 .size().reset_index(name="total_rides")
                 .sort_values("total_rides", ascending=False)
                 .head(10))

avg_dow = (df.groupby(["day_of_week","member_casual"])["ride_length"]
             .mean().reset_index(name="avg_length"))
avg_dow["day_name"] = avg_dow["day_of_week"].map(DOW_NAMES)

hourly     = (df.groupby(["hour_of_day","member_casual"])
               .size().reset_index(name="total_rides"))

# KPIs
total_rides   = len(df)
member_count  = len(df[df["member_casual"] == "member"])
casual_count  = len(df[df["member_casual"] == "casual"])
member_avg    = df[df["member_casual"] == "member"]["ride_length"].mean()
casual_avg    = df[df["member_casual"] == "casual"]["ride_length"].mean()

# ── Construction des figures ───────────────────────────────────────────────────

def styled_fig(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#202124", family="Google Sans, Arial"),
                   x=0.02, xanchor="left"),
        paper_bgcolor=CARD_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family="Google Sans, Arial", size=13, color="#5F6368"),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(size=13)),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    fig.update_xaxes(gridcolor="#E8EAED", linecolor="#E8EAED")
    fig.update_yaxes(gridcolor="#E8EAED", linecolor="#E8EAED")
    return fig

# Fig 1 — Nombre de trajets
fig1 = go.Figure()
for _, row in counts.iterrows():
    fig1.add_trace(go.Bar(
        x=[row["member_casual"].capitalize()],
        y=[row["total_rides"]],
        name=row["member_casual"].capitalize(),
        marker_color=COLOR_MAP[row["member_casual"]],
        text=[f"{row['total_rides']:,}"],
        textposition="outside",
        hovertemplate="%{x}<br>Trajets: %{y:,}<extra></extra>"
    ))
fig1 = styled_fig(fig1, "Nombre total de trajets")
fig1.update_layout(showlegend=False, barmode="group")
fig1.update_yaxes(title_text="Nombre de trajets")

# Fig 2 — Durée moyenne
fig2 = go.Figure()
for _, row in avg_len.iterrows():
    fig2.add_trace(go.Bar(
        x=[row["member_casual"].capitalize()],
        y=[round(row["avg_min"], 1)],
        name=row["member_casual"].capitalize(),
        marker_color=COLOR_MAP[row["member_casual"]],
        text=[f"{row['avg_min']:.1f} min"],
        textposition="outside",
        hovertemplate="%{x}<br>Durée moy.: %{y:.1f} min<extra></extra>"
    ))
fig2 = styled_fig(fig2, "Durée moyenne des trajets (minutes)")
fig2.update_layout(showlegend=False)
fig2.update_yaxes(title_text="Minutes")

# Fig 3 — Trajets par jour de la semaine
fig3 = go.Figure()
for user_type in ["member", "casual"]:
    sub = dow[dow["member_casual"] == user_type].copy()
    sub = sub.set_index("day_name").reindex(dow_order).reset_index()
    fig3.add_trace(go.Bar(
        x=list(sub["day_name"]), y=list(sub["total_rides"]),
        name=user_type.capitalize(),
        marker_color=COLOR_MAP[user_type],
        hovertemplate="%{x}<br>%{y:,} trajets<extra></extra>"
    ))
fig3 = styled_fig(fig3, "Trajets par jour de la semaine")
fig3.update_layout(barmode="group")
fig3.update_yaxes(title_text="Nombre de trajets")

# Fig 4 — Trajets par mois (line)
fig4 = go.Figure()
for user_type in ["member", "casual"]:
    sub = monthly[monthly["member_casual"] == user_type].reset_index(drop=True)
    fig4.add_trace(go.Scatter(
        x=list(sub["period"]), y=list(sub["total_rides"]),
        mode="lines+markers",
        name=user_type.capitalize(),
        line=dict(color=COLOR_MAP[user_type], width=3),
        marker=dict(size=7),
        hovertemplate="%{x}<br>%{y:,} trajets<extra></extra>"
    ))
fig4 = styled_fig(fig4, "Évolution mensuelle des trajets")
fig4.update_layout(xaxis_tickangle=-45)
fig4.update_yaxes(title_text="Nombre de trajets")

# Fig 5 — Types de vélos
fig5 = make_subplots(rows=1, cols=2,
                     subplot_titles=["Membres", "Casual"],
                     specs=[[{"type":"pie"}, {"type":"pie"}]])
colors_pie = [COLOR_MEMBER, COLOR_CASUAL, "#FBBC04", "#EA4335"]
for i, user_type in enumerate(["member", "casual"], 1):
    sub = bikes[bikes["member_casual"] == user_type]
    fig5.add_trace(go.Pie(
        labels=sub["rideable_type"],
        values=sub["total_rides"],
        name=user_type.capitalize(),
        marker_colors=colors_pie,
        hole=0.45,
        textinfo="percent+label",
        hovertemplate="%{label}<br>%{value:,} trajets (%{percent})<extra></extra>"
    ), row=1, col=i)
fig5 = styled_fig(fig5, "Types de vélos utilisés")
fig5.update_layout(showlegend=True)

# Fig 6 — Top 10 stations casual (cible marketing)
fig6 = go.Figure(go.Bar(
    x=top10_casual["total_rides"],
    y=top10_casual["start_station_name"],
    orientation="h",
    marker_color=COLOR_CASUAL,
    text=top10_casual["total_rides"].apply(lambda x: f"{x:,}"),
    textposition="outside",
    hovertemplate="%{y}<br>%{x:,} trajets casual<extra></extra>"
))
fig6 = styled_fig(fig6, "Top 10 stations — Casual riders (cibles marketing)")
fig6.update_layout(yaxis=dict(autorange="reversed"))
fig6.update_xaxes(title_text="Nombre de trajets casual")

# Fig 8 — Durée moyenne par jour de la semaine
fig8 = go.Figure()
for user_type in ["member", "casual"]:
    sub = avg_dow[avg_dow["member_casual"] == user_type].copy()
    sub = sub.set_index("day_name").reindex(dow_order).reset_index()
    fig8.add_trace(go.Bar(
        x=list(sub["day_name"]), y=list(sub["avg_length"].round(1)),
        name=user_type.capitalize(),
        marker_color=COLOR_MAP[user_type],
        hovertemplate="%{x}<br>Durée moy.: %{y:.1f} min<extra></extra>"
    ))
fig8 = styled_fig(fig8, "Durée moyenne des trajets par jour de la semaine")
fig8.update_layout(barmode="group")
fig8.update_yaxes(title_text="Minutes (moyenne)")

# Fig 7 — Trajets par heure
fig7 = go.Figure()
for user_type in ["member", "casual"]:
    sub = hourly[hourly["member_casual"] == user_type].reset_index(drop=True)
    fig7.add_trace(go.Scatter(
        x=list(sub["hour_of_day"]), y=list(sub["total_rides"]),
        mode="lines+markers",
        name=user_type.capitalize(),
        line=dict(color=COLOR_MAP[user_type], width=2.5),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(26,115,232,0.12)" if user_type == "member" else "rgba(52,168,83,0.12)",
        hovertemplate="Heure %{x}h<br>%{y:,} trajets<extra></extra>"
    ))
fig7 = styled_fig(fig7, "Répartition des trajets par heure de départ")
fig7.update_xaxes(title_text="Heure", dtick=2)
fig7.update_yaxes(title_text="Nombre de trajets")

# ── Conversion des figures en HTML partiel ─────────────────────────────────────
def fig_to_div(fig, div_id):
    return pio.to_html(fig, full_html=False, include_plotlyjs=False, div_id=div_id)

divs = {
    "fig1": fig_to_div(fig1, "fig1"),
    "fig2": fig_to_div(fig2, "fig2"),
    "fig3": fig_to_div(fig3, "fig3"),
    "fig4": fig_to_div(fig4, "fig4"),
    "fig5": fig_to_div(fig5, "fig5"),
    "fig6": fig_to_div(fig6, "fig6"),
    "fig7": fig_to_div(fig7, "fig7"),
    "fig8": fig_to_div(fig8, "fig8"),
}

# ── HTML complet ───────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cyclistic — Analyse Bike-Share Chicago</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: "Google Sans", Arial, sans-serif; background: #F1F3F4; color: #202124; }}

  /* Header */
  .header {{
    background: linear-gradient(135deg, #1A73E8 0%, #0D47A1 100%);
    color: white; padding: 32px 48px; display: flex;
    align-items: center; justify-content: space-between;
  }}
  .header h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
  .header p  {{ font-size: 14px; opacity: 0.85; margin-top: 6px; }}
  .badge {{
    background: rgba(255,255,255,0.2); border-radius: 20px;
    padding: 6px 16px; font-size: 13px; white-space: nowrap;
  }}

  /* KPI Cards */
  .kpi-row {{
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 16px; padding: 24px 48px 0;
  }}
  .kpi-card {{
    background: white; border-radius: 12px; padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
  }}
  .kpi-label {{ font-size: 12px; color: #5F6368; text-transform: uppercase;
                letter-spacing: 0.5px; margin-bottom: 8px; }}
  .kpi-value {{ font-size: 26px; font-weight: 700; }}
  .kpi-sub   {{ font-size: 12px; color: #9AA0A6; margin-top: 4px; }}
  .kpi-member {{ color: #1A73E8; }}
  .kpi-casual {{ color: #34A853; }}
  .kpi-total  {{ color: #202124; }}

  /* Grille de graphiques */
  .section-title {{
    padding: 28px 48px 0; font-size: 18px; font-weight: 600; color: #202124;
  }}
  .charts-grid {{
    display: grid; gap: 16px; padding: 16px 48px;
  }}
  .grid-2 {{ grid-template-columns: 1fr 1fr; }}
  .grid-1 {{ grid-template-columns: 1fr; }}
  .chart-card {{
    background: white; border-radius: 12px; padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12); min-height: 420px;
  }}
  .chart-card .plotly-graph-div {{ width: 100% !important; min-height: 400px; }}

  /* Footer */
  .footer {{
    text-align: center; padding: 32px; color: #9AA0A6; font-size: 12px;
  }}

  /* Responsive */
  @media (max-width: 900px) {{
    .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    .grid-2  {{ grid-template-columns: 1fr; }}
    .header, .kpi-row, .filters, .charts-grid, .section-title {{ padding-left: 16px; padding-right: 16px; }}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div>
    <h1>Cyclistic Bike-Share — Chicago</h1>
    <p>Analyse comparative : Membres annuels vs Riders occasionnels | Données 2019–2020</p>
  </div>
  <div class="badge">🚲 {total_rides:,} trajets analysés</div>
</div>

<!-- KPI CARDS -->
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Trajets totaux</div>
    <div class="kpi-value kpi-total">{total_rides:,}</div>
    <div class="kpi-sub">2019–2020</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Membres</div>
    <div class="kpi-value kpi-member">{member_count:,}</div>
    <div class="kpi-sub">{member_count/total_rides*100:.1f}% du total</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Casual riders</div>
    <div class="kpi-value kpi-casual">{casual_count:,}</div>
    <div class="kpi-sub">{casual_count/total_rides*100:.1f}% du total</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Durée moy. Membres</div>
    <div class="kpi-value kpi-member">{member_avg:.1f} min</div>
    <div class="kpi-sub">par trajet</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Durée moy. Casual</div>
    <div class="kpi-value kpi-casual">{casual_avg:.1f} min</div>
    <div class="kpi-sub">par trajet ({casual_avg/member_avg:.1f}x plus long)</div>
  </div>
</div>

<!-- SECTION 1 : VUE D'ENSEMBLE -->
<div class="section-title">Vue d'ensemble</div>
<div class="charts-grid grid-2">
  <div class="chart-card">{divs["fig1"]}</div>
  <div class="chart-card">{divs["fig2"]}</div>
</div>

<!-- SECTION 2 : TEMPOREL -->
<div class="section-title">Analyse temporelle</div>
<div class="charts-grid grid-1">
  <div class="chart-card">{divs["fig4"]}</div>
</div>
<div class="charts-grid grid-2">
  <div class="chart-card">{divs["fig3"]}</div>
  <div class="chart-card">{divs["fig7"]}</div>
</div>

<!-- SECTION 3 : COMPORTEMENT -->
<div class="section-title">Comportement & Équipement</div>
<div class="charts-grid grid-2">
  <div class="chart-card">{divs["fig8"]}</div>
  <div class="chart-card">{divs["fig5"]}</div>
</div>

<!-- SECTION 4 : STATIONS -->
<div class="section-title">Stations</div>
<div class="charts-grid grid-1">
  <div class="chart-card">{divs["fig6"]}</div>
</div>

<!-- FOOTER -->
<div class="footer">
  Cyclistic Case Study — Google Data Analytics Certificate &nbsp;|&nbsp;
  Données : Divvy / Motivate International Inc. &nbsp;|&nbsp;
  Analyse : Python + Plotly
</div>

</body>
</html>"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard généré : {OUT_HTML}")
print("Ouvre ce fichier dans un navigateur pour voir le dashboard interactif.")
