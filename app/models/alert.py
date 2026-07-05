import uuid
from sqlalchemy import Column, String, Float, Text, DateTime
from datetime import datetime
from app.models.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_json = Column(Text, nullable=False)
    normalised_json = Column(Text, nullable=True)
    technique_id = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
