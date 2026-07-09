from sqlalchemy import Column, String, Text
from sqlalchemy.types import JSON

from app.models.database import Base

class Technique(Base):
    __tablename__ = "techniques"

    technique_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    tactics = Column(JSON)
    data_sources = Column(JSON)

    