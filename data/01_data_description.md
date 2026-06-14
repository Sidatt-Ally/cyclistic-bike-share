# 01 — Description des données Cyclistic

## Vue d'ensemble

| Fichier | Période | Lignes | Schéma |
|---|---|---|---|
| Divvy_Trips_2019_Q1.csv | Jan–Mar 2019 | 365 069 | Legacy (2019) |
| Divvy_Trips_2020_Q1.csv | Jan–Mar 2020 | 426 887 | Standard (2020+) |
| 202004-divvy-tripdata.csv | Avril 2020 | 84 776 | Standard (2020+) |
| 202005-divvy-tripdata.csv | Mai 2020 | 200 274 | Standard (2020+) |
| 202006-divvy-tripdata.csv | Juin 2020 | 343 005 | Standard (2020+) |
| 202007-divvy-tripdata.csv | Juillet 2020 | 551 480 | Standard (2020+) |
| 202008-divvy-tripdata.csv | Août 2020 | 622 361 | Standard (2020+) |
| 202009-divvy-tripdata.csv | Septembre 2020 | 532 958 | Standard (2020+) |
| 202010-divvy-tripdata.csv | Octobre 2020 | 388 653 | Standard (2020+) |
| 202011-divvy-tripdata.csv | Novembre 2020 | 259 716 | Standard (2020+) |
| 202012-divvy-tripdata.csv | Décembre 2020 | 131 573 | Standard (2020+) |
| **TOTAL** | **Jan 2019 – Déc 2020** | **~3 906 752** | |

---

## Schémas de colonnes

### Schéma Standard (2020+) — 10 fichiers
```
ride_id            : identifiant unique du trajet (string)
rideable_type      : type de vélo (classic_bike, docked_bike, electric_bike)
started_at         : datetime de début (YYYY-MM-DD HH:MM:SS)
ended_at           : datetime de fin
start_station_name : nom de la station de départ
start_station_id   : identifiant station départ
end_station_name   : nom de la station d'arrivée
end_station_id     : identifiant station arrivée
start_lat          : latitude départ
start_lng          : longitude départ
end_lat            : latitude arrivée
end_lng            : longitude arrivée
member_casual      : type d'utilisateur (member / casual)
```

### Schéma Legacy (2019 Q1) — 1 fichier
```
trip_id            : → ride_id
start_time         : → started_at
end_time           : → ended_at
bikeid             : → pas d'équivalent direct (identifiant vélo)
tripduration       : durée en secondes (fournie, à recalculer)
from_station_id    : → start_station_id
from_station_name  : → start_station_name
to_station_id      : → end_station_id
to_station_name    : → end_station_name
usertype           : → member_casual (Subscriber=member, Customer=casual)
gender             : colonne absente du schéma 2020 (supprimée)
birthyear          : colonne absente du schéma 2020 (supprimée)
```

---

## Qualité des données — Observations préliminaires

### Valeurs manquantes attendues
- `start_station_name` / `end_station_name` : ~5–15% manquants (rides en docked/electric sans ancrage)
- `start_station_id` / `end_station_id` : idem
- `end_lat` / `end_lng` : quelques cas où le vélo n'a pas été redéposé

### Anomalies connues
- **ride_length négatif** : quand `ended_at < started_at` (erreur système) → à supprimer
- **ride_length = 0** : vélos sortis et immédiatement reposés → à supprimer
- **Trajets très longs** (>24h) : probablement des vélos non retournés → à marquer/filtrer
- **Stations HQ QR** : trajets de maintenance internes Cyclistic → à supprimer

### Cohérence inter-fichiers
- Le fichier 2019 Q1 utilise `Subscriber`/`Customer` au lieu de `member`/`casual` → mapping requis
- Le type de vélo (`rideable_type`) n'existe pas dans le fichier 2019 Q1 → valeur `unknown`

---

## Colonnes créées lors du nettoyage

| Colonne | Description | Source |
|---|---|---|
| `ride_length` | Durée du trajet en minutes | `ended_at - started_at` |
| `day_of_week` | Jour de la semaine (1=Dim, 7=Sam) | `started_at` |
| `month` | Mois (1–12) | `started_at` |
| `year` | Année | `started_at` |
| `season` | Saison (Spring/Summer/Fall/Winter) | `month` |
| `hour_of_day` | Heure de départ (0–23) | `started_at` |

---

## Sources des données

- **Fournisseur** : Motivate International Inc. pour la ville de Chicago
- **Licence** : [Divvy Data License Agreement](https://www.divvybikes.com/data-license-agreement)
- **Note RGPD** : données anonymisées — aucune info personnelle identifiable
- **Limites** : impossible de relier les trajets à un utilisateur spécifique (pas de carte de paiement)
