import os


from fastapi import APIRouter, HTTPException
import requests
from app.models.database import SessionLocal
from app.models.playbook_db import Playbook

from app.utils.logger import logger

router = APIRouter(prefix="/shuffle", tags=["shuffle"])

SHUFFLE_URL = "https://localhost:3443/api/v1/workflows"
api_key = os.getenv("SHUFFLE_API_KEY")


@router.post("/import/{playbook_id}")
def import_workflow(playbook_id: str):

    """
    Import an approved playbook into the local
    Shuffle automation platform.
    """

    db = SessionLocal()

    try:
        playbook = (
            db.query(Playbook)
            .filter(Playbook.id == playbook_id)
            .first()
    )
    finally:
        db.close()

    if not playbook:
        raise HTTPException(

            status_code=404,
            detail="Playbook not found"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            SHUFFLE_URL,
            headers=headers,
            data=playbook.playbook_json,
            verify=False,
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
    logger.info(
        "shuffle_import_started",
        extra={
            "playbook_id": playbook_id
        }
    )
    logger.info(
        "shuffle_import_success",
        extra={
            "playbook_id": playbook_id
        }
    )
    return {
        "message": "Workflow imported successfully."
    }
