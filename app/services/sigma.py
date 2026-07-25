from pydantic import BaseModel, Field

class AlertInput(BaseModel):
    sender: str = Field(
        description="Email address of the alert sender",
        examples=["analyst@example.com"]
    )
    subject: str
    body_text: str = Field(
        description="Security alert body",
        examples=["PowerShell executed encoded command from explorer.exe"]
    )
    severity: int = 5
    source_system: str