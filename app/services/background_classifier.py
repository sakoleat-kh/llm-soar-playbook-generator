from pathlib import Path

from app.models.database import SessionLocal
from app.models.alert import Alert
from app.models.playbook_db import Playbook

from app.services.classifier import classify_alert
from app.services.playbook import generate_playbook
from app.services.renderer import render_shuffle_workflow

def classify_alert_background(alert_id: str) -> None:

    db = SessionLocal()

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if alert is None:
            return
        
        result = classify_alert(alert.normalised_json)

        alert.technique_id = result.technique_id
        alert.confidence = result.confidence

        draft = generate_playbook(
            technique_id=result.technique_id,
            technique_name=result.technique_name,
            alert_summary=alert.normalised_json,
        )
        print("\n==== PLAYBOOK DRAFT ====")
        print(draft.model_dump())

        workflow = render_shuffle_workflow(
            draft=draft,
            alert_id=alert.id,
        )

        playbook = Playbook(
            technique_id = draft.technique_id,
            technique_name = draft.technique_name,
            playbook_json = workflow,
        )

        db.add(playbook)
        db.commit()
        db.refresh(playbook)

        print(f"playbook saved with ID: {playbook.id}")

        output_dir = Path("generated_workflows")
        output_dir.mkdir(exist_ok=True)

        workflow_path = output_dir / f"{alert.id}.json"

        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(workflow)
        print(f"workflow saved: {workflow_path}")

        db.commit()

    finally:
        db.close()
