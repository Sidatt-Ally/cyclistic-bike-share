# 07 — Guide Tableau : Dashboard Cyclistic

## Prérequis

- Tableau Desktop ou **Tableau Public** (gratuit)
- Fichier source : `data/processed/cyclistic_tableau.csv`
- Générer ce fichier en exécutant : `python scripts/06_tableau_export.py`

---

## Colonnes disponibles dans cyclistic_tableau.csv

| Colonne | Type Tableau | Description |
|---|---|---|
| `ride_id` | String (Dimension) | Identifiant unique |
| `member_casual` | String (Dimension) | `member` ou `casual` |
| `member_label` | String (Dimension) | `Member` ou `Casual` (affichage) |
| `rideable_type` | String (Dimension) | Type de vélo |
| `started_at` | Date/Heure (Dimension) | Début du trajet |
| `ended_at` | Date/Heure (Dimension) | Fin du trajet |
| `start_date` | Date (Dimension) | Date de départ (YYYY-MM-DD) |
| `ride_length` | Number (Measure) | Durée en **minutes** |
| `ride_length_hms` | String | Durée en HH:MM:SS |
| `day_of_week` | Number (Dimension) | 1=Dimanche … 7=Samedi |
| `day_name` | String (Dimension) | Nom du jour en anglais |
| `is_weekend` | Boolean/Number | 1=Week-end, 0=Semaine |
| `month` | Number (Dimension) | 1–12 |
| `month_name` | String (Dimension) | Nom du mois en anglais |
| `year` | Number (Dimension) | 2019 ou 2020 |
| `season` | String (Dimension) | Spring / Summer / Fall / Winter |
| `start_hour` | Number (Dimension) | Heure de départ (0–23) |
| `start_station_name` | String (Dimension) | Station de départ |
| `end_station_name` | String (Dimension) | Station d'arrivée |
| `start_lat` / `start_lng` | Number (Geographic) | Coordonnées départ |
| `end_lat` / `end_lng` | Number (Geographic) | Coordonnées arrivée |

---

## Étape 1 — Connexion aux données

1. Ouvrir Tableau Desktop / Tableau Public
2. **Connect > Text File** → sélectionner `cyclistic_tableau.csv`
3. Dans l'écran de prévisualisation, vérifier les types :
   - `started_at`, `ended_at` → **Date & Time**
   - `ride_length` → **Number (decimal)**
   - `start_lat`, `start_lng`, `end_lat`, `end_lng` → **Number (decimal)**
   - `day_of_week`, `month`, `year` → **Number (whole)**
   - Tout le reste → **String**

---

## Étape 2 — Paramètre de filtre utilisateur

Crée un paramètre pour filtrer par type d'utilisateur :
1. **Clic droit** dans le panneau Data → **Create Parameter**
2. Nom : `User Type Filter`
3. Data type : **String**
4. Allowable values : **List** → Ajouter : `All`, `Member`, `Casual`
5. Current value : `All`
6. Clic **OK**

Crée un Calculated Field `User Filter` :
```
[Parameter.User Type Filter] = "All"
OR UPPER([member_label]) = UPPER([Parameter.User Type Filter])
```
Utilise ce champ comme filtre sur chaque feuille.

---

## Étape 3 — Visualisations à créer

### Sheet 1 — Rides Count (Bar Chart)
- **Rows :** `member_label`
- **Columns :** `CNT(ride_id)`
- **Color :** `member_label`
- Couleurs : Member = `#1A73E8`, Casual = `#34A853`
- **Label :** Afficher les valeurs
- Titre : *"Total Rides by User Type"*

### Sheet 2 — Avg Ride Length (Bar Chart)
- **Rows :** `member_label`
- **Columns :** `AVG(ride_length)`
- **Color :** `member_label`
- **Format :** 1 décimale + "min"
- Titre : *"Average Ride Duration (minutes)"*

### Sheet 3 — Rides by Day of Week (Grouped Bar)
- **Columns :** `day_name`
- **Rows :** `CNT(ride_id)`
- **Color :** `member_label`
- **Sort :** `day_of_week` croissant (pour ordre Dim→Sam)
- Marks : **Bar**, side-by-side
- Titre : *"Rides by Day of Week"*

### Sheet 4 — Monthly Trend (Line Chart)
- Glisser `started_at` sur **Columns**, choisir **Month** (discret ou continu)
- **Rows :** `CNT(ride_id)`
- **Color :** `member_label`
- Marks : **Line**
- Titre : *"Monthly Ride Trends"*

### Sheet 5 — Bike Types (Bar Chart)
- **Columns :** `rideable_type`
- **Rows :** `CNT(ride_id)`
- **Color :** `member_label`
- Marks : **Bar**, stacked ou side-by-side
- Titre : *"Bike Type Usage"*

### Sheet 6 — Top 10 Start Stations (Horizontal Bar)
- Glisser `start_station_name` → **Rows**
- `CNT(ride_id)` → **Columns**
- Filtre : Top 10 par `CNT(ride_id)` (**Filter > Top > By Field**)
- **Sort :** Descending
- Titre : *"Top 10 Start Stations"*

### Sheet 7 — Map des stations (Map View)
- Double-cliquer sur `start_lat` → Tableau génère automatiquement une carte
- Glisser `start_lng` sur **Columns** si nécessaire
- **Size :** `CNT(ride_id)` (taille des points proportionnelle au volume)
- **Color :** `member_label`
- Titre : *"Station Heatmap"*

### Sheet 8 — Rides by Hour (Line Chart)
- **Columns :** `start_hour`
- **Rows :** `CNT(ride_id)`
- **Color :** `member_label`
- Marks : **Line**
- Titre : *"Rides by Hour of Day"*

---

## Étape 4 — Dashboard

1. Clic sur l'icône **New Dashboard** (bas de l'écran)
2. Taille : **Automatic** ou **1200 × 900 px**
3. Disposition suggérée :

```
┌─────────────────────────────────────────┐
│  TITRE + KPI CARDS (Text objects)       │
├──────────────┬──────────────────────────┤
│ Sheet 1      │ Sheet 2                  │
│ (Rides Count)│ (Avg Duration)           │
├──────────────┴──────────────────────────┤
│ Sheet 3 — Rides by Day of Week          │
├─────────────────────────────────────────┤
│ Sheet 4 — Monthly Trend (full width)    │
├──────────────┬──────────────────────────┤
│ Sheet 5      │ Sheet 6                  │
│ (Bike Types) │ (Top Stations)           │
├─────────────────────────────────────────┤
│ Sheet 7 — Map (full width)              │
└─────────────────────────────────────────┘
```

4. Ajouter le paramètre `User Type Filter` :
   - **Dashboard menu > Actions > Filter** → lier à toutes les sheets
   - Ou afficher le contrôle du paramètre : clic droit sur le paramètre → **Show Parameter**

5. Couleurs globales : **Format > Workbook** → définir palette personnalisée

---

## Étape 5 — Publication sur Tableau Public

1. **File > Save to Tableau Public**
2. Créer un compte gratuit sur public.tableau.com si nécessaire
3. Nommer : *"Cyclistic Bike-Share Analysis 2019-2020"*
4. Copier le lien de partage pour ton portfolio

---

## Champs calculés utiles à créer dans Tableau

```
// Durée en heures (pour les trajets longs)
Ride Length Hours = [ride_length] / 60

// Étiquette durée formatée
Ride Length Label = 
  STR(INT([ride_length])) + " min " + 
  STR(INT(([ride_length] - INT([ride_length])) * 60)) + " sec"

// Indicateur week-end (si colonne absente)
Is Weekend = [day_of_week] = 1 OR [day_of_week] = 7

// Segment utilisateur enrichi
User Segment = 
  IF [member_casual] = "member" AND [is_weekend] = 0 THEN "Member Weekday"
  ELSEIF [member_casual] = "member" AND [is_weekend] = 1 THEN "Member Weekend"
  ELSEIF [member_casual] = "casual" AND [is_weekend] = 0 THEN "Casual Weekday"
  ELSE "Casual Weekend"
  END
```
