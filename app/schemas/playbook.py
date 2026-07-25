from pydantic import BaseModel, Field

class RejectRequest(BaseModel):
    reason: str = Field(
        description="Reason for rejecting the playbook",
        examples=["Fales positive"]
    )