from pydantic import BaseModel, Field

class DetectLeagueInput(BaseModel):
    team: str = Field(
        description="Team name, can be in Chinese or English"    
    )