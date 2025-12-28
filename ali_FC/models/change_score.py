from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ChangeScoreInput(BaseModel):
    match: list[dict] = Field(
        description="List of match records"
    )
    home_score: int = Field(
        description="The goal number of home team"
    )
    away_score: int = Field(
        description="The goal number of away team"
    )