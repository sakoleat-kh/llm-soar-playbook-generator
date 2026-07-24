from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.routers.shuffle import import_workflow

from app.models.database import SessionLocal
from app.models.playbook_db import Playbook

from app.schemas.playbook import RejectRequest

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

        try:
            import_workflow(playbook.id)
            playbook.import_status = "imported"
        except Exception:
            playbook.import_status = "failed"
            raise
        db.commit()

        return{
            "message": "Playbook approved and imported successfully.",
            "status": playbook.status
        }
    finally:
        db.close()

@router.post("/{alert_id}/reject")
def reject_playbook(
    alert_id: str,
    request: RejectRequest
    ):

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

        print("==========")
        print("Reason:", request.reason)
        print("==========")

        playbook.rejection_reason = request.reason

        db.commit()

        return {
            "message": "Playbook rejected.",
            "status": playbook.status
        }

    finally:
        db.close()