from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryMatchesInput(BaseModel):
    matches: List[Dict[str, Any]] = Field(
        description="List of match records"
    )
    team: str = Field(
        description="Team name to query"
    )
    date: Optional[str] = Field(
        default=None,
        description="Date filter (YYYY-MM-DD)"
    )
    result: Optional[str] = Field(
        default=None,
        description="win / lose / draw"
    )
    home_or_away: Optional[str] = Field(
        default=None,
        description="home or away"
    )