from pydantic import BaseModel, Field

class DeleteMatchesInput(BaseModel):
    matches: list[dict] = Field(
        description="List of match records"
    )