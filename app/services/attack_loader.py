import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.database import Base, SessionLocal, engine
from app.models.technique import Technique

Base.metadata.create_all(bind=engine)

def load_all_techniques():

    """
    Load MITRE ATT&CK techniques from the Enterprise ATT&CK JSON file
    into the local database, skipping revoked and existing techniques.
    """

    json_file = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "enterprise-attack.json"
    )

    print(json_file)
    print(json_file.exists())

    with open(json_file, "r", encoding="utf-8") as f:
        attack_data = json.load(f)

    print("Objects:", len(attack_data["objects"]))

    db: Session = SessionLocal()

    try:
        count = 0

        for obj in attack_data["objects"]:

            if obj.get("type") != "attack-pattern":
                continue

            if obj.get("revoked", False):
                continue

            technique_id = None

            for ref in obj.get("external_references", []):

                if ref.get("source_name") == "mitre-attack":
                    technique_id = ref.get("external_id")
                    break

            if technique_id is None:
                continue

            existing = db.get(Technique, technique_id)

            if existing:
                continue

            tactics = [
                phase.get("phase_name")
                for phase in obj.get("kill_chain_phases", [])
                ]

            technique = Technique(
                    technique_id=technique_id,
                    name=obj.get("name", ""),
                    description=obj.get("description", ""),
                    tactics=tactics,
                    data_sources=obj.get(
                        "x_mitre_data_sources",
                        [],
                    ),
                )

            db.add(technique)
            print(technique_id, obj.get("name"))
            count += 1

        db.commit()

        print(f"Loaded {count} techniques.")

    finally:
        db.close()

if __name__ == "__main__":
    load_all_techniques()
