import uuid
from sqlalchemy import Column, String, Float, Text, DateTime
from datetime import datetime
from app.models.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    technique_id = Column(String, nullable=True)
    technique_name = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    raw_json = Column(Text, nullable=False)
    normalised_json = Column(Text, nullable=True)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    classification_path = Column(String, nullable=True)
    classification_error = Column(Text, nullable=True)

