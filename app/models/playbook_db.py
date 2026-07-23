from sqlalchemy import Column, Integer, String, Text

from app.models.database import Base

class Playbook(Base):
    __tablename__ = "playbook"

    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(String, nullable=False)
    technique_name = Column(String, nullable=False)
    playbook_json = Column(Text, nullable=False)
    

