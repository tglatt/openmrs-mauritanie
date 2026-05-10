# Mauritania Health Module

Instance OpenMRS 3 configurée pour les centres de santé mauritaniens.

## Fonctionnalités

- Interface en français (support arabe prévu)
- Concepts médicaux : température, poids, tension, diagnostic, traitement, paludisme
- Types de rencontres : Consultation, Triage, Laboratoire, Pharmacie, Maternité, Vaccination
- Rôles utilisateurs : Réceptionniste, Infirmier, Médecin, Pharmacien, Laborantin, Administrateur
- Localisations : Nouakchott, Nuadhibou et centres de santé associés
- Attributs patients : NNI, téléphone, Wilaya, Commune
- Configuration chargée automatiquement via Initializer au démarrage

## Structure

```
mauritania-health-module/
├── docker-compose.yml              # Stack Docker OpenMRS 3
├── config-mauritania.json          # Configuration frontend (langue, modules UI)
└── configuration/                  # Chargée par Initializer au démarrage
    ├── concepts/                   # Concepts médicaux
    ├── encountertypes/             # Types de rencontres
    ├── roles/                      # Rôles utilisateurs et privilèges
    ├── locations/                  # Établissements de santé
    └── personattributetypes/       # Attributs patients (NNI, Wilaya…)
```

## Prérequis

- Docker et Docker Compose

## Démarrage

```bash
docker-compose up -d
```

Accès : http://localhost/openmrs

La configuration (concepts, rôles, localisations) est importée automatiquement par le module Initializer au premier démarrage.

## Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `TAG` | `qa` | Tag des images OpenMRS 3 |
| `OMRS_DB_USER` | `openmrs` | Utilisateur base de données |
| `OMRS_DB_PASSWORD` | `openmrs` | Mot de passe base de données |
| `MYSQL_ROOT_PASSWORD` | `openmrs` | Mot de passe root MariaDB |

Exemple avec un tag précis :

```bash
TAG=3.7.x docker-compose up -d
```

## Personnalisation

### Langue
La locale par défaut est `fr`. Elle est définie dans `docker-compose.yml` (`SPA_DEFAULT_LOCALE`) et dans `config-mauritania.json`.

### Configuration frontend
Modifier `config-mauritania.json` pour ajuster les modules, le nom de l'instance ou les champs du formulaire d'enregistrement patient.

### Ajouter des données de référence
Ajouter des fichiers CSV dans `configuration/` — ils seront chargés automatiquement au prochain démarrage du backend.

## Stack technique

| Service | Image |
|---|---|
| Reverse proxy | `openmrs/openmrs-reference-application-3-gateway` |
| Frontend SPA | `openmrs/openmrs-reference-application-3-frontend` |
| Backend OpenMRS | `openmrs/openmrs-reference-application-3-backend` |
| Base de données | `mariadb:10.11.7` |
