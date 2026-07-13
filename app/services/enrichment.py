from typing import Optional
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.technique import Technique

def get_technique_detail(technique_id: str) -> Optional[dict]:
    db: Session = SessionLocal()

    try: 
        technique = (
            db.query(Technique)
            .filter(Technique.technique_id == technique_id)
            .first()
        )

        if technique is None:
            return None
        
        prefix = f"{technique_id}."

        sub_techniques = (
            db.query(Technique.technique_id)
            .filter(Technique.technique_id.like(f"{prefix}%"))
            .all()
        )

        return {
            "technique_id":  technique.technique_id,
            "name": technique.name,
            "description": technique.description,
            "tactics": technique.tactics or [],
            "data_sources": technique.data_sources or [],
            "sub_techniques": [row.technique_id for row in sub_techniques],
        }
    
    finally:
        db.close()
    