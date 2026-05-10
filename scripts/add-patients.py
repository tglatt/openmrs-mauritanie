#!/usr/bin/env python3
"""Script de création de 100 patients fictifs pour OpenMRS Mauritanie."""

import random
import json
import urllib.request
import urllib.error
import base64
from datetime import date, timedelta

OPENMRS_URL = "http://localhost/openmrs/ws/rest/v1"
USERNAME = "admin"
PASSWORD = "Admin123"
NB_PATIENTS = 100

PRENOMS_MASCULINS = [
    "Mohamed", "Ahmed", "Abdallah", "Ibrahim", "Ismail", "Oumar", "Sidi",
    "Cheikh", "Mamadou", "Moussa", "Yahya", "Youssef", "Hassan", "Hamidou",
    "Abdel", "Mokhtar", "Brahim", "Saleh", "Ould", "Tijani", "Boubacar",
    "Alioune", "Amadou", "Demba", "Aliou"
]

PRENOMS_FEMININS = [
    "Fatimata", "Mariam", "Aissata", "Aminata", "Maimouna", "Khadija",
    "Zeinabou", "Halima", "Oumou", "Ndeye", "Fatoumata", "Rokhaya",
    "Coumba", "Adja", "Astou", "Ramatoulaye", "Salimata", "Hawa", "Dieynaba"
]

NOMS_DE_FAMILLE = [
    "Ould Mohamed", "Ould Ahmed", "Ould Ibrahim", "Ba", "Diallo", "Sy",
    "Kane", "Sow", "Coulibaly", "Traore", "Camara", "Sarr", "Ndiaye",
    "Fall", "Mbaye", "Cissé", "Konaté", "Maiga", "Touré", "Keita",
    "Mint Mohamed", "Mint Ahmed", "Mint Brahim", "Ould Cheikh", "Ould Sidi"
]

LOCATIONS = [
    "ba583e51-0eb2-4f78-b116-4d82822f910c",  # Centre de Santé de Néma
]


def make_request(endpoint, method="GET", data=None):
    url = f"{OPENMRS_URL}/{endpoint}"
    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  Erreur {e.code}: {e.read().decode()[:200]}")
        return None


def random_date(start_year=1950, end_year=2010):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_nni():
    return str(random.randint(1000000000, 9999999999))


def create_patient(index):
    gender = random.choice(["M", "F"])
    if gender == "M":
        given_name = random.choice(PRENOMS_MASCULINS)
    else:
        given_name = random.choice(PRENOMS_FEMININS)

    family_name = random.choice(NOMS_DE_FAMILLE)
    birthdate = random_date()
    nni = generate_nni()

    patient_data = {
        "person": {
            "names": [{"givenName": given_name, "familyName": family_name}],
            "gender": gender,
            "birthdate": birthdate.strftime("%Y-%m-%d"),
            "addresses": [{"country": "Mauritanie"}],
        },
        "identifiers": [
            {
                "identifier": nni,
                "identifierType": "3cf646c3-6bb4-4c61-aba0-ef338b5e21ee",
                "location": random.choice(LOCATIONS),
                "preferred": True,
            }
        ],
    }

    result = make_request("patient", method="POST", data=patient_data)
    if result and "uuid" in result:
        print(f"  [{index:3d}/100] ✓ {given_name} {family_name} ({gender}, {birthdate.year}) NNI:{nni}")
        return True
    else:
        print(f"  [{index:3d}/100] ✗ Échec pour {given_name} {family_name}")
        return False


def main():
    print(f"Création de {NB_PATIENTS} patients fictifs...\n")
    success = 0
    for i in range(1, NB_PATIENTS + 1):
        if create_patient(i):
            success += 1

    print(f"\n{'='*50}")
    print(f"Résultat : {success}/{NB_PATIENTS} patients créés avec succès.")


if __name__ == "__main__":
    main()
