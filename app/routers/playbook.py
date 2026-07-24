from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.playbook_db import Playbook

router = APIRouter(prefix="/playbooks", tags=["playbooks"])

@router.get("/{alert_id}")
def get_playbook(alert_id: str):

    db = SessionLocal()

    playbook = (
        db.query(Playbook)
        .filter(Playbook.alert_id == alert_id)
        .first()
    )

    if playbook is None:
        raise HTTPException(
            status_code=404,
            detail="Playbook not found"
        )

    return playbook

@router.post("/{alert_id}/approve")
def approve_playbook(alert_id: str):
    db = SessionLocal()

    try:
        playbook = (
            db.query(Playbook)
            .filter(Playbook.alert_id == alert_id)
            .first()
        )

        if playbook is None:
            raise HTTPException(status_code=404, detail="Playbook not found")

        playbook.status = "approved"

        db.commit()

        return{
            "message": "Playbook approved successfully.",
            "status": playbook.status
        }
    finally:
        db.close()

@router.post("/{alert_id}/reject")
def reject_playbook(alert_id: str):

    db = SessionLocal()

    try:
        playbook = (
            db.query(Playbook)
            .filter(Playbook.alert_id == alert_id)
            .first()
        )

        if playbook is None:
            raise HTTPException(
                status_code=404,
                detail="Playbook not found"
            )
        playbook.status = "rejected"

        db.commit()

        return {
            "massage": "Playbook rejected.",
            "status": playbook.status
        }

    finally:
        db.close()