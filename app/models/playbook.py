import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.models.database import Base

class Playbook(Base):
    __tablename__ = "playbooks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    playbook_json = Column(Text, nullable=False)
    sigma_rules = Column(Text, nullable=True)
    import_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    