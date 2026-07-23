from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.alert import Alert
from app.services.normaliser import normalise_alert
from app.services.sigma import AlertInput
from app.services.background_classifier import classify_alert_background

router = APIRouter()

@router.post("/webhook/alert")
def recive_alert(
    alert: AlertInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Normalise the incoming alert
    normalised_alert = normalise_alert(alert)

    # Create database record
    db_alert = Alert(
        raw_json=alert.model_dump_json(),
        normalised_json=normalised_alert.model_dump_json()
    )

    # Save to SQLite
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    background_tasks.add_task(
        classify_alert_background,
        db_alert.id
    )

    # Return generated alert ID
    return {
        "status": "received",
        "alert_id": db_alert.id
    }
    
@router.get("/alerts")
def list_alerts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    limit = min(limit, 100)

    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return alerts

@router.get("/alerts/{alert_id}")
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )
    return alert

