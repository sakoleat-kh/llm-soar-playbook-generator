from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.routers.shuffle import import_workflow

from app.models.database import SessionLocal
from app.models.playbook_db import Playbook

from app.schemas.playbook import RejectRequest

from app.utils.logger import logger

router = APIRouter(prefix="/playbooks", tags=["playbooks"])

@router.get(
    "/{alert_id}",
    summary="Get Playbook",
    description="Returns the generated playbook for the specified alert.",
    response_description="The generated playbook.",
    responses={
        404: {
            "description": "Playbook not found"
        }
    }
    )
def get_playbook(alert_id: str):

    """
    Retrieve the generated playbook associated with 
    the specified alert.
    """

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

@router.post(
    "/{alert_id}/approve",
    summary="Approve Playbook",
    description="Approves a generated playbook and import and it into Shuffle.",
    response_description="Approval result.",
    responses={
        404: {
            "description": "Playbook not found"
        },
        503: {
            "description": "Shuffle import failed"
        }
    }
    )
def approve_playbook(alert_id: str):

    """
    Approve a generated playbook, import it into Shuffle,
    and update its approval status.
    """

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

        logger.info(
            "playbook_approved",
            extra={
                "alert_id": alert_id
            }
        )

        return{
            "message": "Playbook approved and imported successfully.",
            "status": playbook.status
        }
    finally:
        db.close()

@router.post(
    "/{alert_id}/reject",
    summary="Reject Playbook",
    description="Rejects a generated playbook and stores the rejection reason.",
    response_description="Rejection result.",
    responses={
        404: {
            "description": "Playbook not found"
        },
    }
)
def reject_playbook(
    alert_id: str,
    request: RejectRequest
    ):

    """
    Reject a generated playbook and store the 
    analyst's rejection reason.
    """

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

        logger.info(
            "playbook_rejected",
            extra={
                "alert_id": alert_id,
                "reason": request.reason
            }
        )

        return {
            "message": "Playbook rejected.",
            "status": playbook.status
        }

    finally:
        db.close()