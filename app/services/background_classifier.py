from pathlib import Path
import traceback

from app.models.database import SessionLocal
from app.models.alert import Alert
from app.models.playbook_db import Playbook

from app.services.classifier import classify_alert
from app.services.playbook import generate_playbook
from app.services.renderer import render_shuffle_workflow


def classify_alert_background(alert_id: str):

    print("=" * 60)
    print("BACKGROUND TASK STARTED")
    print(alert_id)
    print("=" * 60)

    db = SessionLocal()

    try:

        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if alert is None:
            print("Alert not found")
            return

        print("Alert loaded")

        print("Running classifier...")
        result = classify_alert(alert.normalised_json)

        print("Classifier finished")
        print(result)

        alert.technique_id = result.technique_id
        alert.technique_name = result.technique_name
        alert.confidence = result.confidence
        alert.status = "classified"

        db.commit()

        print("Alert updated")

        print("Generating playbook...")

        draft = generate_playbook(
            technique_id=result.technique_id,
            technique_name=result.technique_name,
            alert_summary=alert.normalised_json,
        )

        print("Playbook generated")

        workflow = render_shuffle_workflow(
            draft=draft,
            alert_id=alert.id,
        )

        playbook = Playbook(
            alert_id=alert_id,
            technique_id=draft.technique_id,
            technique_name=draft.technique_name,
            playbook_json=workflow,
        )

        db.add(playbook)
        db.commit()

        print("Playbook saved")

        output_dir = Path("generated_workflows")
        output_dir.mkdir(exist_ok=True)

        workflow_path = output_dir / f"{alert.id}.json"

        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(workflow)

        print("Workflow written")

    except Exception:

        print("\n\nBACKGROUND TASK FAILED\n")
        traceback.print_exc()

    finally:

        db.close()
        print("BACKGROUND TASK FINISHED")