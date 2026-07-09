from attackcti import attack_client
from sqlalchemy.orm import Session

from app.models.database import Base, SessionLocal, engine
from app.models.technique import Technique

# Ensure the table exits 
Base.metadata.create_all(bind=engine)

def load_all_techniques():
    client = attack_client()
    techniques = client.get_techniques()

    db: Session = SessionLocal()

    try:
        for tech in techniques:
            technique_id = tech.get("external_references", [{}])[0].get("external_id")
            if not technique_id:
                continue
            existing = db.get(Technique, technique_id)
            if existing:
                continue

            tactics = [
                phase.get("phase_name")
                for phase in tech.get("kill_chain_phases", [])
            ]
            data_sources = tech.get("x_mitre_data_sources", [])

            technique = Technique(
                technique_id=technique_id,
                name=tech.get("name", ""),
                description=tech.get("description", ""),
                tactics=tactics,
                data_sources=data_sources,
            )

            db.add(technique)

        db.commit()
        print("MITRE ATT&CK techniques loaded successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    load_all_techniques()
