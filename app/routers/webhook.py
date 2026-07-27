from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.alert import Alert
from app.services.normaliser import normalise_alert
from app.services.sigma import AlertInput
from app.services.background_classifier import classify_alert_background
from app.utils.logger import logger


router = APIRouter()


@router.post(
    "/webhook/alert",
    summary="Receive Security Alert",
    description="Received a security alert, normalizes it, stores it in the database, and start background classification.",
    response_description="Returns the generated alert ID."

    )
def receive_alert(
    alert: AlertInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    """
    Receive a security alert, normalize it, store it,
    and start background classification.
    """
    
    if not alert.body_text.strip():
        raise HTTPException(
            status_code=400,
            detail="body_text cannot be empty."
        )

    MAX_ALERT_SIZE = 5000

    print(f"Alert lenght = {len(alert.body_text)}")

    if len(alert.body_text) > MAX_ALERT_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Alert exceeds maximun length."
        )

    existing = (
        db.query(Alert)
        .filter(Alert.raw_json == alert.model_dump_json())
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Duplicate alert."
        )
    
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

    logger.info(
        "alert_received",
        extra={
            "alert_id": db_alert.id,
            "path": "webhook"
        }
    )

    background_tasks.add_task(
        classify_alert_background,
        db_alert.id
    )

    # Return generated alert ID
    return {
        "status": "received",
        "alert_id": db_alert.id
    }
    
@router.get(
    "/alerts",
    summary="List Alert",
    description="Returns the latest alerts stored in the database.",
    response_description="A list of alerts."

    )
def list_alerts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):

    """
    Return the most recent alerts stored in the database.
    """
    
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

    """
    Return a single alert using its unique identifier.
    """
    
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

