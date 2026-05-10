# OpenMRS Mauritanie

Instance OpenMRS 3 configurée pour la gestion des centres de santé mauritaniens.

## Fonctionnalités

- Interface en français (support arabe prévu)
- Hiérarchie d'adresses : Wilaya → Moughataa → Commune (15 wilayas, toutes moughataas)
- Localisations : 100+ centres de santé et hôpitaux avec codes FOSA
- Identifiant patient : NNI (Numéro National d'Identité, 10 chiffres, unique)
- Types de consultation liés aux registres du Ministère de la Santé
- Concepts médicaux CIEL + concepts spécifiques Mauritanie
- Attributs patients : NNI, téléphone
- Formulaires O3 : Consultation Externe
- Configuration chargée automatiquement via Initializer au démarrage

## Structure

```
openmrs-mauritanie/
├── docker-compose.yml
├── config-mauritania.json              # Configuration frontend O3
├── configuration/                      # Chargée par Initializer au démarrage
│   ├── addresshierarchy/
│   │   ├── addressConfiguration.xml   # Niveaux : Pays > Wilaya > Moughataa > Commune
│   │   └── addresshierarchy.csv       # ~140 entrées géographiques
│   ├── ampathforms/
│   │   └── consultation-externe.json  # Formulaire O3 consultation externe
│   ├── attributetypes/
│   │   └── attributetypes.csv         # Code FOSA (attribut location)
│   ├── concepts/
│   │   └── concepts.csv               # Concepts CIEL + concepts MR spécifiques
│   ├── encountertypes/
│   │   └── encountertypes.csv         # 10 registres : Consultation, CPN, Accouchement...
│   ├── globalproperties/
│   │   └── globalproperties.xml       # Locale fr, pays MR, NNI par défaut
│   ├── locations/
│   │   └── locations.csv              # Wilayas, moughataas, hôpitaux, CS avec UUIDs
│   ├── patientidentifiertypes/
│   │   └── patientidentifiertypes.csv # NNI (10 chiffres, unique)
│   ├── personattributetypes/
│   │   └── personattributetypes.csv   # NNI, Téléphone
│   ├── roles/
│   │   └── roles.csv
│   └── visittypes/
│       └── visittypes.csv             # Facility Visit, OPD Visit
└── temp/
    └── registres/                     # Registres source du Ministère de la Santé (JSON)
```

## Registres configurés

| # | Registre | Encounter Type |
|---|---|---|
| 01 | Consultation Externe | Consultation |
| 02 | Hospitalisation | Admission / Discharge |
| 03 | Chirurgie | Chirurgie |
| 04 | Laboratoire | Lab Results |
| 05 | CPN | CPN |
| 06 | Accouchement | Accouchement |
| 07 | CPON | CPON |
| 08 | Planification Familiale | Planification Familiale |
| 09 | Urgences Obstétricales | Urgences Obstétricales |
| 10 | Décès Maternels et Néonataux | Décès Maternel et Néonatal |

## Prérequis

- Docker et Docker Compose

## Démarrage

```bash
docker compose up -d
```

Accès : http://localhost/openmrs/spa

Login par défaut : `admin` / `Admin1234`

La configuration est importée automatiquement par l'Initializer au premier démarrage.

## Commandes utiles

```bash
# Suivre les logs de l'Initializer
docker compose logs -f backend | grep -i "initializer\|ERROR\|WARN"

# Repartir d'une base propre (supprime toutes les données)
docker compose down -v && docker compose up -d

# Utiliser un tag d'image précis
TAG=3.7.0 docker compose up -d
```

## Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `TAG` | `qa` | Tag des images OpenMRS 3 |
| `OMRS_DB_USER` | `openmrs` | Utilisateur base de données |
| `OMRS_DB_PASSWORD` | `openmrs` | Mot de passe base de données |
| `MYSQL_ROOT_PASSWORD` | `openmrs` | Mot de passe root MariaDB |

## Stack technique

| Service | Image |
|---|---|
| Reverse proxy | `openmrs/openmrs-reference-application-3-gateway` |
| Frontend SPA | `openmrs/openmrs-reference-application-3-frontend` |
| Backend OpenMRS | `openmrs/openmrs-reference-application-3-backend` |
| Base de données | `mariadb:10.11.7` |
