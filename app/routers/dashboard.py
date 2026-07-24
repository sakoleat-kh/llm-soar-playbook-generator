from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import get_db
from app.models.alert import Alert
from app.models.playbook_db import Playbook

import json

router = APIRouter()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):

    alerts = (
        db.query(Alert)
        .order_by(desc(Alert.created_at))
        .limit(20)
        .all()
    )

    results = []

    for alert in alerts:

        playbook = (
            db.query(Playbook)
            .filter(Playbook.alert_id == alert.id)
            .first()
        )

        alert_type = "Unknown"

        if alert.raw_json:
            try:
                raw = json.loads(alert.raw_json)

                print("========== RAW JSON ==========")
                print(raw)
                print("==============================")

                if isinstance(raw, dict):
                    body = raw.get("body_text", "")

                    if "ALERT NAME:" in body:
                        for line in body.splitlines():
                            if line.startswith("ALERT NAME:"):
                                alert_type = line.replace("ALERT NAME:", "").strip()
                                break

                    elif body:
                        alert_type = body

                    else:
                        alert_type = raw.get("subject", "Unknown")

            except Exception as e:
                print("JSON Error:", e)

        results.append(
            {
                "id": alert.id,
                "timestamp": alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "alert_type": alert_type,
                "technique": alert.technique_name,
                "confidence": (
                    round(alert.confidence * 100, 1)
                    if alert.confidence is not None
                    else 0
                ),
                "status": (
                    playbook.status
                    if playbook
                    else "pending"
                ),
            }
        )

    return results