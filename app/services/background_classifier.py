from app.models.database import SessionLocal
from app.models.alert import Alert
from app.services.classifier import classify_alert

def classify_alert_background(alert_id: str) -> None:

    db = SessionLocal()

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if alert is None:
            return
        
        result = classify_alert(alert.normalised_json)

        alert.technique_id = result.technique_id
        alert.confidence = result.confidence

        db.commit()

    finally:
        db.close()
