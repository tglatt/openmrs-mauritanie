# OpenMRS Mauritanie

Instance OpenMRS 3 configurée pour le Centre de Santé de Néma (Mauritanie).

## Fonctionnalités

- Interface en français (support arabe prévu)
- Hiérarchie géographique : Mauritanie → Hodh Ech Chargui → Néma → Centre de Santé de Néma
- Identifiant patient : NNI (Numéro National d'Identité, 10 chiffres, unique)
- Types de consultation liés aux registres du Ministère de la Santé
- Concepts médicaux CIEL + concepts spécifiques Mauritanie
- File d'attente (Triage / Consultation) avec priorités et statuts
- Rendez-vous : 4 services (Consultation Externe, CPN, Vaccination, PF) avec 9 types
- Modes de paiement adaptés (Espèces, Mobile Money, CNAM, etc.)
- Formulaires O3 : Consultation Externe
- Configuration chargée automatiquement via Initializer au démarrage

## Structure

```
openmrs-mauritanie/
├── Dockerfile                              # Image backend custom (sans configs demo)
├── docker-compose.yml
├── config-mauritania.json                  # Configuration frontend O3
├── assets/
│   └── logo-msas.png                       # Logo Ministère de la Santé
├── scripts/
│   ├── add-patients.py                     # Crée 100 patients fictifs mauritaniens
│   └── add-visits-appointments.py          # Crée 10 visites actives + 100 RDV (semaine à venir)
└── configuration/                          # Chargée par Initializer au démarrage
    ├── addresshierarchy/
    │   ├── addressConfiguration.xml        # Niveaux : Pays > Wilaya > Moughataa > Commune
    │   └── addresshierarchy.csv            # ~140 entrées géographiques
    ├── ampathforms/
    │   └── consultation-externe.json       # Formulaire O3 consultation externe
    ├── appointmentservicedefinitions/
    │   └── service_definitions.csv         # 4 services au Centre de Santé de Néma
    ├── appointmentservicetypes/
    │   └── service_types.csv               # 9 types de RDV
    ├── appointmentspecialities/
    │   └── specialities.csv                # Spécialité : Soins de Santé Primaires
    ├── attributetypes/
    │   └── attributetypes.csv              # Code FOSA, Insurance Policy Number, Punctuality
    ├── concepts/
    │   ├── concepts.csv                    # Concepts CIEL + concepts MR spécifiques
    │   ├── queue-concepts.csv              # Concepts file d'attente (priorités, statuts, services)
    │   └── [fichiers referenceapplication] # Concepts extraits de la référenceapplication
    ├── conceptsources/
    │   └── conceptsources.csv              # Source CIEL
    ├── encountertypes/
    │   └── encountertypes.csv              # 16 types : Consultation, CPN, Accouchement...
    ├── globalproperties/
    │   └── globalproperties.xml            # Locale fr, pays MR, NNI par défaut, queues
    ├── locations/
    │   └── locations.csv                   # Mauritanie > Hodh Ech Chargui > Néma > CS Néma
    ├── patientidentifiertypes/
    │   └── patientidentifiertypes.csv      # NNI (10 chiffres, unique)
    ├── paymentmodes/
    │   └── paymentmodes.csv                # Espèces, Chèque, Virement, Mobile Money, CNAM...
    ├── personattributetypes/
    │   └── personattributetypes.csv        # NNI, Téléphone
    ├── queues/
    │   └── queues.csv                      # Files d'attente Triage et Consultation
    ├── roles/
    │   └── roles.csv
    └── visittypes/
        └── visittypes.csv                  # Facility Visit, OPD Visit
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

## Services de rendez-vous

| Service | Types de RDV |
|---|---|
| Consultation Externe | Nouvelle consultation, Suivi, Urgence |
| CPN | 1ère CPN, CPN de suivi |
| Vaccination | Primo-vaccination, Rappel |
| Planification Familiale | Initiation PF, Suivi PF |

## Modes de paiement

| Mode | Description |
|---|---|
| Espèces | Paiement cash |
| Chèque | Chèque bancaire |
| Virement bancaire | Transfert bancaire |
| Mobile Money (Masrivi) | Paiement mobile mauritanien |
| Assurance maladie (CNAM) | Caisse Nationale d'Assurance Maladie |
| Prise en charge gratuite | Gratuité (urgences, indigents) |

## Prérequis

- Docker et Docker Compose
- Python 3 (pour les scripts de données fictives)

## Démarrage

```bash
# Premier démarrage (construction de l'image custom)
docker compose up -d --build

# Accès
http://localhost/openmrs/spa
```

Login par défaut : `admin` / `Admin123`

La configuration est importée automatiquement par l'Initializer (~15 min au premier démarrage).

## Données de test

```bash
# 1. Créer 100 patients fictifs mauritaniens
python3 scripts/add-patients.py

# 2. Créer 10 visites actives + 100 RDV sur la semaine à venir
python3 scripts/add-visits-appointments.py
```

## Commandes utiles

```bash
# Suivre les logs de l'Initializer
docker compose logs -f backend 2>&1 | grep -E "Initializer|ERROR|WARN"

# Redémarrer le backend seulement (pour recharger la configuration sans vider la DB)
docker compose restart backend

# Repartir d'une base propre (supprime toutes les données)
docker compose down && docker volume rm openmrs-mauritanie_openmrs-data openmrs-mauritanie_db-data && docker compose up -d

# Vérifier les erreurs de chargement de configuration
docker compose logs backend 2>&1 | grep -A 6 "could not be constructed"
```

## Architecture

### Images Docker

| Service | Image | Version |
|---|---|---|
| Reverse proxy | `openmrs/openmrs-reference-application-3-gateway` | `3.6.0` |
| Frontend SPA | `openmrs/openmrs-reference-application-3-frontend` | `3.6.0` |
| Backend OpenMRS | Image custom basée sur `openmrs-reference-application-3-backend` | `3.6.0` |
| Base de données | `mariadb` | `10.11.7` |

L'image backend est construite via le `Dockerfile` local qui supprime les configurations de la référenceapplication pour ne charger que la configuration mauritanienne.

### Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `OMRS_DB_USER` | `openmrs` | Utilisateur base de données |
| `OMRS_DB_PASSWORD` | `openmrs` | Mot de passe base de données |
| `MYSQL_ROOT_PASSWORD` | `openmrs` | Mot de passe root MariaDB |

### Notes sur le déploiement multi-sites

Cette configuration est conçue pour le développement avec **une seule FOSA** (Centre de Santé de Néma). Pour un déploiement en production, l'architecture recommandée est **une instance par FOSA** avec synchronisation vers un serveur central, afin de garantir le fonctionnement en mode hors-ligne dans les zones à connectivité limitée (Hodh, Tagant, Adrar…).
