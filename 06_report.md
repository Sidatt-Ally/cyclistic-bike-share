# Cyclistic Bike-Share — Rapport d'Analyse
## Comment les membres annuels et les riders occasionnels utilisent-ils les vélos différemment ?

**Auteur :** Junior Data Analyst — Cyclistic Marketing Analytics Team
**Date :** Juin 2026
**Destinataire :** Lily Moreno, Director of Marketing

---

## 1. Énoncé de la Business Task

**Question principale :** Comment les membres annuels et les riders occasionnels utilisent-ils les vélos Cyclistic différemment ?

**Contexte :** Cyclistic, programme de bike-share à Chicago (5 800+ vélos, 692 stations), dispose de deux types d'utilisateurs :
- **Members** : abonnement annuel, plus rentables selon les analystes financiers
- **Casual riders** : pass journée ou trajet unique

**Objectif business :** Concevoir une stratégie marketing pour convertir les casual riders en membres annuels. Les recommandations doivent être appuyées par des données solides et des visualisations professionnelles pour être approuvées par l'équipe exécutive.

**Parties prenantes :**
- Lily Moreno (Director of Marketing) — commanditaire de l'analyse
- Cyclistic Executive Team — décisionnaires finaux
- Cyclistic Marketing Analytics Team — équipe d'implémentation

---

## 2. Sources de données

### Fichiers utilisés

| Fichier | Période | Lignes |
|---|---|---|
| Divvy_Trips_2019_Q1.csv | Jan–Mar 2019 | 365 069 |
| Divvy_Trips_2020_Q1.csv | Jan–Mar 2020 | 426 887 |
| 202004-divvy-tripdata.csv | Avril 2020 | 84 776 |
| 202005-divvy-tripdata.csv | Mai 2020 | 200 274 |
| 202006-divvy-tripdata.csv | Juin 2020 | 343 005 |
| 202007-divvy-tripdata.csv | Juillet 2020 | 551 480 |
| 202008-divvy-tripdata.csv | Août 2020 | 622 361 |
| 202009-divvy-tripdata.csv | Septembre 2020 | 532 958 |
| 202010-divvy-tripdata.csv | Octobre 2020 | 388 653 |
| 202011-divvy-tripdata.csv | Novembre 2020 | 259 716 |
| 202012-divvy-tripdata.csv | Décembre 2020 | 131 573 |
| **Total** | **Jan 2019 – Déc 2020** | **~3 906 752** |

### Crédibilité des données (ROCCC)

| Critère | Évaluation |
|---|---|
| **Reliable** | ✅ Données opérationnelles collectées automatiquement par les capteurs |
| **Original** | ✅ Source primaire : Motivate International Inc. (opérateur réel) |
| **Comprehensive** | ✅ Couvre tous les trajets sur la période, pas d'échantillonnage |
| **Current** | ⚠️ Données 2019–2020 (pas temps réel, mais suffisantes pour les tendances) |
| **Cited** | ✅ Licence publique Divvy Data License Agreement |

### Limites et contraintes
- **Confidentialité** : pas d'identifiant personnel — impossible de relier les trajets à un individu
- **Données manquantes** : ~5–15% de valeurs nulles sur les noms de stations (rides electric/docked)
- **Schéma hétérogène** : le fichier 2019 Q1 utilise une structure différente (mappée lors du nettoyage)
- **COVID-19** : les données 2020 peuvent refléter des comportements atypiques (confinement)

---

## 3. Documentation du nettoyage

### Outils utilisés
- **Python 3.x** avec pandas, numpy (nettoyage + analyse)
- **matplotlib / seaborn** (visualisations statiques)
- **Plotly** (dashboard interactif)

### Transformations appliquées

| Étape | Action | Impact |
|---|---|---|
| Harmonisation schéma | Renommage colonnes 2019 Q1 + mapping Subscriber→member / Customer→casual | Unification des 11 fichiers |
| Conversion datetime | `started_at` et `ended_at` → format datetime | Calculs temporels |
| ride_length | `(ended_at - started_at)` en minutes | Nouvelle colonne |
| day_of_week | 1=Dimanche … 7=Samedi | Nouvelle colonne |
| month / year / season | Extraits de started_at | Nouvelles colonnes |
| Doublons | Suppression sur ride_id | Dédoublonnage |
| ride_length ≤ 0 | Suppression (erreurs système) | Données invalides |
| ride_length > 1440 min | Suppression (vélos non retournés) | Outliers extrêmes |
| Stations de maintenance | Suppression (HQ QR, TEST, DIVVY) | Trajets internes |

> Voir `data/02_cleaning_log.md` pour le log détaillé avec les comptages exacts.

---

## 4. Résumé de l'analyse

> *Note : les chiffres ci-dessous seront mis à jour après exécution de 02_cleaning.py et 03_analysis.py*

### 4.1 Statistiques descriptives globales

| Métrique | Members | Casual |
|---|---|---|
| Nombre de trajets | 2 508 757 | 1 376 682 |
| % du total | 64,6% | 35,4% |
| Durée moyenne | 14,6 min | 37,1 min |
| Durée médiane | 10,6 min | 21,7 min |
| Durée max | 1 439,7 min | 1 439,9 min |

> **Insight clé :** les casual riders font des trajets **2,5× plus longs** en moyenne que les membres, mais ils sont **2× moins nombreux** en volume de trajets. Cela suggère un usage loisir/touristique plutôt que fonctionnel.

### 4.2 Comportement temporel

**Par jour de la semaine :**
- Les **members** sont plus actifs en **semaine** (jeudi = jour de pointe, ~391k trajets) → usage **utilitaire** (domicile-travail)
- Les **casual riders** se concentrent sur le **week-end** (samedi = jour de pointe, ~318k trajets) → usage **loisir**
- Différence structurelle : les membres maintiennent un volume élevé 5 jours/7, les casual ont un profil en cloche autour du week-end

**Par mois / saison :**
- Pic estival (juin–août) pour les deux types
- **Casual : hyper-saisonniers** — Summer = 51,5% de leurs trajets annuels vs 32% pour les membres
- En hiver, les membres restent relativement actifs (556k trajets) vs casual quasi-absents (57k)
- Impact COVID visible : avril 2020 creux pour les deux types (confinement)

**Par heure :**
- **Members** : double pic à 8h et 17h (rush hours) → trajet domicile-travail confirmé
- **Casual** : montée progressive dès 10h, pic à 15–17h → loisir, tourisme, pas d'urgence horaire

### 4.3 Types de vélos (hors legacy 2019)
- **Docked bikes** dominent pour les deux types (usage standard)
- Les **casual riders** utilisent plus d'**electric bikes** en proportion (14,9% vs 11,8% membres)
- Les membres utilisent légèrement plus de **classic bikes**

### 4.4 Stations
- Les casual riders se concentrent sur des stations touristiques (bords du lac Michigan, parcs)
- Les membres utilisent des stations dans les quartiers résidentiels et de bureaux
- Jour de pointe : **Jeudi** pour les membres, **Samedi** pour les casual

---

## 5. Visualisations clés

Tous les graphiques sont disponibles dans le dossier `figures/` :

| Fichier | Description |
|---|---|
| `01_rides_count.png` | Nombre total de trajets membres vs casual |
| `02_avg_ride_length.png` | Durée moyenne des trajets |
| `03_rides_by_dow.png` | Trajets par jour de la semaine |
| `04_rides_by_month.png` | Évolution mensuelle |
| `05_bike_types.png` | Types de vélos utilisés |
| `06_top10_stations.png` | Top 10 stations de départ |
| `07_rides_by_hour.png` | Répartition par heure |
| `08_avg_length_by_dow.png` | Durée moyenne par jour |

**Dashboard interactif :** `05_dashboard.html` (ouvrir dans un navigateur)

---

## 6. Top 3 Recommandations Marketing

### Recommandation 1 — Campagne "Week-end → Abonnement" ciblée géographiquement

**Insight :** Les casual riders utilisent principalement les vélos le week-end, sur des stations touristiques (bords du lac, parcs).

**Action :** Lancer une campagne digitale ciblant les utilisateurs dans un rayon de 500m autour des stations à forte fréquentation casual (lakefront, Navy Pier, Millennium Park). Afficher des publicités sur les réseaux sociaux le vendredi soir et samedi matin avec le message : *"Tu roules déjà le week-end — économise avec l'abonnement annuel."*

**Canaux :** Instagram/TikTok géolocalisés, notifications in-app Cyclistic

---

### Recommandation 2 — Offre d'essai "Été → Membre" à tarif préférentiel

**Insight :** Les casual riders sont très saisonniers avec un pic estival. C'est le meilleur moment pour les convertir.

**Action :** Proposer en mai–juin une offre d'abonnement annuel avec les 2 premiers mois offerts ou un tarif réduit de lancement pour les utilisateurs ayant effectué 3+ trajets en 30 jours. Envoyer un email personnalisé : *"Tu as déjà utilisé Cyclistic X fois ce mois-ci — tu aurais économisé Y€ avec un abonnement."*

**Canaux :** Email ciblé, notification push in-app, bannières dans l'app

---

### Recommandation 3 — Mettre en avant la valeur "domicile-travail" dans les communications

**Insight :** Les membres utilisent les vélos principalement pour les trajets domicile-travail (pics 8h et 17h en semaine). Les casual riders ignorent peut-être cet usage.

**Action :** Créer du contenu montrant que l'abonnement annuel devient rentable à partir de X trajets/mois pour un navetteur. Intégrer un calculateur d'économies dans l'app et sur le site : *"Si tu fais X trajets par semaine, l'abonnement te coûte Y€/trajet vs Z€ en pass journée."*

**Canaux :** Content marketing (blog, réseaux sociaux), campagne d'affichage dans les stations aux heures de pointe

---

## Appendice

- **Script de nettoyage :** `scripts/02_cleaning.py`
- **Script d'analyse :** `scripts/03_analysis.py`
- **Requêtes SQL :** `scripts/03_queries.sql`
- **Script visualisations :** `scripts/04_visualizations.py`
- **Script dashboard :** `scripts/05_dashboard.py`
- **Export Tableau :** `scripts/06_tableau_export.py`
- **Données nettoyées :** `data/processed/cyclistic_clean.csv`
- **Export Tableau :** `data/processed/cyclistic_tableau.csv`
