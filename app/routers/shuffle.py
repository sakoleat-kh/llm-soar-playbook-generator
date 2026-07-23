from fastapi import APIRouter, HTTPException
import requests
from app.models.database import SessionLocal
from app.models.playbook_db import Playbook


router = APIRouter(prefix="/shuffle", tags=["shuffle"])

SHUFFLE_URL = "http://localhost:3443/api/v1/workflows"
SHUFFLE_API_KEY = "Your API KEY"

@router.post("/import/{playbook_id}")
def import_workflow(playbook_id: str):
    db = SessionLocal()

    playbook = (
        db.query(Playbook)
        .filter(Playbook.id == playbook_id)
        .first()
    )
    print(playbook)

    if not playbook:
        raise HTTPException(

            status_code=404,
            detail="Playbook not found"
        )

    headers = {
        "Authorization": f"Bearer {SHUFFLE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            SHUFFLE_URL,
            headers=headers,
            data=playbook.playbook_json,
            timeout=30,
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Shuffle server is not running."
        )

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=401,
            detail="Shuffle authentication failed."
        )
    if response.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail="Workflow already exists."
        )
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    return {
        "message": "Workflow imported successfully."
    }
