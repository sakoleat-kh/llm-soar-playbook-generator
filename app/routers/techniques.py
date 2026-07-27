from fastapi import APIRouter, HTTPException

from app.services.enrichment import get_technique_detail

router = APIRouter(prefix="/techniques", tags=["Techniques"])

@router.get("/{technique_id}")
def technique_detail(technique_id: str):

    """
    Return detailed information about a MITRE ATT&CK 
    technique from the local database.
    """

    technique = get_technique_detail(technique_id)

    if technique is None:
        raise HTTPException(
            status_code=404,
            detail="Technique not found",
        )
    return technique