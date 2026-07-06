from pydantic import BaseModel

class AlertInput(BaseModel):
    sender: str
    subject: str
    body_text: str
    severity: int = 5
    source_system: str