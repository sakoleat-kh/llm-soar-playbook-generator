from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter()

class AlertInput(BaseModel):
    sender: str
    subject: str
    body_text: str
    severity : int = 5
    source_system: str

@router.post("/webhook/alert")
async def recive_webhook(alert: AlertInput):
    return{
        "status": "recieved",
        "alert_id": str(uuid4())
    }