#!/usr/bin/env python3
"""Crée des utilisateurs médecins avec leurs providers associés."""

import json
import urllib.request
import urllib.error
import base64

OPENMRS_URL = "http://localhost/openmrs/ws/rest/v1"
USERNAME = "admin"
PASSWORD = "Admin123"

MEDECIN_ROLE = "Médecin"

MEDECINS = [
    {
        "givenName": "Elkhalil",
        "familyName": "Ishagh",
        "gender": "M",
        "username": "elkhalil.ishagh",
        "password": "Medecin123!",
        "identifier": "MED-001",
    },
    {
        "givenName": "Chadi",
        "familyName": "Mhedhebi",
        "gender": "M",
        "username": "chadi.mhedhebi",
        "password": "Medecin123!",
        "identifier": "MED-002",
    },
]


def make_request(endpoint, method="GET", data=None):
    url = f"{OPENMRS_URL}/{endpoint}"
    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Erreur {e.code}: {body[:300]}")
        return None


def create_medecin(m):
    name = f"{m['givenName']} {m['familyName']}"
    print(f"\n→ Création de Dr {name}...")

    # 1. Créer la personne
    person = make_request("person", method="POST", data={
        "names": [{"givenName": m["givenName"], "familyName": m["familyName"]}],
        "gender": m["gender"],
    })
    if not person or "uuid" not in person:
        print(f"  ✗ Échec création personne")
        return False
    person_uuid = person["uuid"]
    print(f"  ✓ Personne créée : {person_uuid}")

    # 2. Créer l'utilisateur
    user = make_request("user", method="POST", data={
        "username": m["username"],
        "password": m["password"],
        "person": person_uuid,
        "roles": [{"name": MEDECIN_ROLE}],
    })
    if not user or "uuid" not in user:
        print(f"  ✗ Échec création utilisateur")
        return False
    print(f"  ✓ Utilisateur créé : {m['username']} / {m['password']}")

    # 3. Créer le provider
    provider = make_request("provider", method="POST", data={
        "person": person_uuid,
        "identifier": m["identifier"],
        "retired": False,
    })
    if not provider or "uuid" not in provider:
        print(f"  ✗ Échec création provider")
        return False
    print(f"  ✓ Provider créé : {m['identifier']}")

    return True


def main():
    print("Création des utilisateurs médecins...\n")
    success = 0
    for m in MEDECINS:
        if create_medecin(m):
            success += 1

    print(f"\n{'='*50}")
    print(f"Résultat : {success}/{len(MEDECINS)} médecins créés.")
    print(f"\nIdentifiants de connexion :")
    for m in MEDECINS[:success]:
        print(f"  - {m['username']} / {m['password']}")


if __name__ == "__main__":
    main()
