#!/usr/bin/env python3
"""Crée 10 visites actives et 100 rendez-vous sur la semaine à venir."""

import random
import json
import urllib.request
import urllib.error
import base64
from datetime import date, datetime, timedelta

OPENMRS_URL = "http://localhost/openmrs/ws/rest/v1"
USERNAME = "admin"
PASSWORD = "Admin123"

LOCATION_UUID   = "ba583e51-0eb2-4f78-b116-4d82822f910c"
VISIT_TYPE_UUID = "7b0f5697-27e3-40c4-8bae-f4049abfb4ed"  # Facility Visit

# Services et leurs types de RDV
SERVICES = [
    {
        "uuid": "69ed267f-9e5d-4a2e-93ff-47b555781797",
        "name": "Consultation Externe",
        "types": [
            "1d4799bd-a2ad-4159-a389-47bfa13fc6aa",  # Nouvelle consultation
            "7b0c0290-2d8c-4928-8b89-819c6a3f692c",  # Suivi
            "2cdb0780-6f94-4e4e-a171-7bdaa565f339",  # Urgence
        ],
    },
    {
        "uuid": "33904042-96a5-4d00-a558-ea0006126f2e",
        "name": "CPN",
        "types": [
            "bab6641e-b092-4b1f-b2e6-a2ef15910ff1",  # 1ère CPN
            "0fc80aee-e5d5-4c4e-9474-eb94fbf6c8a4",  # CPN de suivi
        ],
    },
    {
        "uuid": "894c0534-a604-40e7-8a26-e3c66e6728e1",
        "name": "Vaccination",
        "types": [
            "3097f591-4a40-45ca-ab34-b5f549eb6610",  # Primo-vaccination
            "5b3adf52-bb7a-42d1-95cf-dc011a7cf56c",  # Rappel
        ],
    },
    {
        "uuid": "fe4f06d1-920f-4c86-b226-37a079f99400",
        "name": "Planification Familiale",
        "types": [
            "a1c65c3b-2e7d-4169-9c4f-e81e7a7fc74f",  # Initiation PF
            "17913d7f-b8bd-4629-96c5-769f17915979",  # Suivi PF
        ],
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
        print(f"  Erreur {e.code}: {e.read().decode()[:300]}")
        return None


def get_patients(limit=100):
    seen = set()
    patients = []
    for letter in ["ma", "fa", "ha", "sa", "ka", "ba", "al", "ou", "di", "mo"]:
        result = make_request(f"patient?q={letter}&v=default&limit={limit}")
        for p in (result.get("results", []) if result else []):
            if p["uuid"] not in seen:
                seen.add(p["uuid"])
                patients.append(p)
        if len(patients) >= limit:
            break
    return patients[:limit]


def create_visit(patient_uuid):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000")
    data = {
        "patient": patient_uuid,
        "visitType": VISIT_TYPE_UUID,
        "location": LOCATION_UUID,
        "startDatetime": now,
    }
    return make_request("visit", method="POST", data=data)


def create_appointment(patient_uuid, appt_date, slot_hour):
    service = random.choice(SERVICES)
    appt_type = random.choice(service["types"])
    start = datetime(appt_date.year, appt_date.month, appt_date.day, slot_hour, 0, 0)
    end   = start + timedelta(minutes=30)

    data = {
        "patientUuid": patient_uuid,
        "serviceUuid": service["uuid"],
        "appointmentKind": "Scheduled",
        "status": "Scheduled",
        "startDateTime": int(start.timestamp() * 1000),
        "endDateTime":   int(end.timestamp() * 1000),
        "locationUuid": LOCATION_UUID,
        "appointmentNumber": str(random.randint(1000, 9999)),
        "comments": "",
    }
    return make_request("appointments", method="POST", data=data)


def main():
    print("Récupération des patients...")
    patients = get_patients(100)
    if not patients:
        print("Aucun patient trouvé. Lance d'abord add-patients.py.")
        return
    print(f"  {len(patients)} patients disponibles.\n")

    # --- 10 visites actives ---
    print("Création de 10 visites actives...")
    visit_patients = random.sample(patients, min(10, len(patients)))
    visits_ok = 0
    for p in visit_patients:
        result = create_visit(p["uuid"])
        if result and "uuid" in result:
            print(f"  ✓ Visite : {p['display']}")
            visits_ok += 1
        else:
            print(f"  ✗ Échec visite : {p['display']}")

    # --- 100 rendez-vous sur 7 jours ---
    print(f"\nCréation de 100 rendez-vous (lun-sam, 8h-16h)...")
    today = date.today()
    # Prochains jours ouvrés (lundi à samedi)
    work_days = []
    d = today + timedelta(days=1)
    while len(work_days) < 6:
        if d.weekday() < 6:  # 0=lundi … 5=samedi
            work_days.append(d)
        d += timedelta(days=1)

    slots = list(range(8, 16))  # 8h à 15h
    appts_ok = 0
    for i in range(1, 101):
        patient = random.choice(patients)
        appt_date = random.choice(work_days)
        slot_hour = random.choice(slots)
        result = create_appointment(patient["uuid"], appt_date, slot_hour)
        if result and ("uuid" in result or "appointmentNumber" in result):
            appts_ok += 1
            print(f"  [{i:3d}/100] ✓ {patient['display']} — {appt_date} {slot_hour}h00")
        else:
            print(f"  [{i:3d}/100] ✗ Échec RDV : {patient['display']}")

    print(f"\n{'='*55}")
    print(f"Visites actives : {visits_ok}/10")
    print(f"Rendez-vous     : {appts_ok}/100")


if __name__ == "__main__":
    main()
