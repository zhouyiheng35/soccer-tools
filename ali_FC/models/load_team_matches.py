from pydantic import BaseModel, Field

class LoadTeamMatchesInput(BaseModel):
    league: str = Field(
        description="League code, e.g. E0 for Premier League"
    )
    team: str = Field(
        description="Team name"
    )