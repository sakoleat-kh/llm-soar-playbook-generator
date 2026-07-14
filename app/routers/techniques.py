from fastapi import APIRouter, HTTPException

from app.services.enrichment import get_technique_detail

router = APIRouter(prefix="/techniques", tags=["Techniques"])

@router.get("/{technique_id}")
def technique_detail(technique_id: str):
    technique = get_technique_detail(technique_id)

    if technique is None:
        raise HTTPException(
            status_code=404,
            detail="Technique not found",
        )
    return technique