from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.alert import Alert
from app.services.normaliser import normalise_alert
from app.services.sigma import AlertInput

router = APIRouter()

# class AlertInput(BaseModel):
#     sender: str
#     subject: str
#     body_text: str
#     severity : int = 5
#     source_system: str

@router.post("/webhook/alert")
async def recive_webhook(
    alert: AlertInput,
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

    # Return generated alert ID
    return {
        "status": "received",
        "alert_id": db_alert.id
    }
    