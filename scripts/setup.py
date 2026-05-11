#!/usr/bin/env python3
"""
Script de configuration post-initialisation OpenMRS Mauritanie.
À lancer après chaque réinitialisation de la base de données.

Usage:
    python3 scripts/setup.py
"""

import json
import urllib.request
import urllib.error
import base64
import time

OPENMRS_URL = "http://localhost/openmrs/ws/rest/v1"
USERNAME = "admin"
PASSWORD = "Admin123"

# Médecins à créer
MEDECINS = [
    {"givenName": "Elkhalil", "familyName": "Ishagh",   "username": "elkhalil.ishagh",  "password": "Medecin123!", "identifier": "MED-001"},
    {"givenName": "Chadi",    "familyName": "Mhedhebi", "username": "chadi.mhedhebi",   "password": "Medecin123!", "identifier": "MED-002"},
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
        return {"error": e.read().decode()[:200]}


def wait_for_backend(retries=20, delay=15):
    print("Attente du démarrage du backend...")
    for i in range(retries):
        result = make_request("session")
        if result and "authenticated" in result:
            print("  ✓ Backend disponible.\n")
            return True
        print(f"  [{i+1}/{retries}] Pas encore prêt, attente {delay}s...")
        time.sleep(delay)
    print("  ✗ Backend inaccessible après les tentatives.")
    return False


def get_role_uuid(name):
    result = make_request("role?v=default&limit=50")
    for r in result.get("results", []):
        if r.get("display") == name:
            return r["uuid"]
    return None


def fix_medecin_role():
    print("=== Configuration du rôle Médecin ===")
    medecin_uuid = get_role_uuid("Médecin")
    infirmier_uuid = get_role_uuid("Infirmier")
    full_uuid = get_role_uuid("Privilege Level: Full")

    if not medecin_uuid:
        print("  ✗ Rôle Médecin introuvable.")
        return False

    print(f"  Médecin UUID : {medecin_uuid}")

    result = make_request(f"role/{medecin_uuid}", method="POST", data={
        "inheritedRoles": [{"uuid": infirmier_uuid}, {"uuid": full_uuid}]
    })
    inherited = [r.get("display") for r in result.get("inheritedRoles", [])]
    if inherited:
        print(f"  ✓ Rôles hérités : {inherited}")
        return True
    else:
        print(f"  ✗ Échec : {result.get('error', '')}")
        return False


def user_exists(username):
    result = make_request(f"user?q={username}&v=default")
    return any(u.get("username") == username for u in result.get("results", []))


def create_medecin(m):
    name = f"{m['givenName']} {m['familyName']}"
    if user_exists(m["username"]):
        print(f"  ↷ Dr {name} existe déjà.")
        return True

    person = make_request("person", method="POST", data={
        "names": [{"givenName": m["givenName"], "familyName": m["familyName"]}],
        "gender": "M",
    })
    if "uuid" not in person:
        print(f"  ✗ Échec création personne pour {name}")
        return False
    person_uuid = person["uuid"]

    user = make_request("user", method="POST", data={
        "username": m["username"],
        "password": m["password"],
        "person": person_uuid,
        "roles": [{"name": "Médecin"}],
    })
    if "uuid" not in user:
        print(f"  ✗ Échec création utilisateur pour {name}")
        return False

    provider = make_request("provider", method="POST", data={
        "person": person_uuid,
        "identifier": m["identifier"],
        "retired": False,
    })
    if "uuid" not in provider:
        print(f"  ✗ Échec création provider pour {name}")
        return False

    print(f"  ✓ Dr {name} créé ({m['username']} / {m['password']})")
    return True


def create_admin_provider():
    print("\n=== Provider pour admin ===")
    result = make_request("user?q=admin&v=full")
    admin = next((u for u in result.get("results", []) if u.get("username") == "admin"), None)
    if not admin:
        print("  ✗ Utilisateur admin introuvable.")
        return

    person_uuid = admin.get("person", {}).get("uuid")
    providers = make_request(f"provider?v=default")
    for p in providers.get("results", []):
        if p.get("person", {}).get("uuid") == person_uuid:
            print(f"  ↷ Provider admin existe déjà.")
            return

    result = make_request("provider", method="POST", data={
        "person": person_uuid,
        "identifier": "ADMIN",
        "retired": False,
    })
    if "uuid" in result:
        print("  ✓ Provider admin créé.")
    else:
        print(f"  ✗ Échec : {result.get('error', '')}")


def fix_numeric_concepts():
    """
    L'Initializer ne supporte pas le flag allow_decimal pour les concepts numériques.
    Ce fix corrige la précision décimale directement en base via l'API SQL interne.
    """
    print("\n=== Correction décimales concepts numériques ===")

    # Concepts qui doivent accepter les décimales
    decimal_uuids = [
        "5088AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Temperature (38.5°C)
        "5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Weight (70.5 kg)
        "5090AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Height (168.5 cm)
        "5096AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # MUAC
        "1342AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # BMI
        "1343AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # MUAC alt
        "5916AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Birth weight
    ]

    fixed = 0
    for uuid in decimal_uuids:
        try:
            result = make_request(f"concept/{uuid}", method="GET")
            if "uuid" not in result:
                continue
            # Patch via admin SQL endpoint
            import subprocess
            cmd = [
                "docker", "exec", "openmrs-mauritanie-db-1",
                "mysql", "-uopenmrs", "-popenmrs", "-e",
                f"USE openmrs; UPDATE concept_numeric cnm JOIN concept c ON c.concept_id=cnm.concept_id SET cnm.allow_decimal=1 WHERE c.uuid='{uuid}';"
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                fixed += 1
        except Exception:
            pass

    if fixed > 0:
        print(f"  ✓ {fixed} concepts mis à jour (allow_decimal=1)")
    else:
        print("  ⚠ Fix via Docker non disponible — lancez manuellement :")
        print("  docker exec openmrs-mauritanie-db-1 mysql -uopenmrs -popenmrs -e \"USE openmrs; UPDATE concept_numeric cnm JOIN concept c ON c.concept_id=cnm.concept_id SET cnm.allow_decimal=1 WHERE c.uuid IN ('5088AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','5090AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','5096AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','1342AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','1343AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA');\"")


def main():
    print("╔══════════════════════════════════════════╗")
    print("║  Setup OpenMRS Mauritanie                ║")
    print("╚══════════════════════════════════════════╝\n")

    if not wait_for_backend():
        return

    fix_medecin_role()

    print("\n=== Création des médecins ===")
    for m in MEDECINS:
        create_medecin(m)

    create_admin_provider()
    fix_numeric_concepts()

    print("\n✓ Configuration terminée.")
    print("\nIdentifiants médecins :")
    for m in MEDECINS:
        print(f"  {m['username']} / {m['password']}")


if __name__ == "__main__":
    main()
