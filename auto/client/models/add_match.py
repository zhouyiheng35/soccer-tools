from pydantic import BaseModel, Field

class AddMatchInput(BaseModel):
    league: str = Field(
        description="The league code(e.g., 'E0', 'D1', ...) which the team belongs to through 'detect_league' tool"
    )
    date: str = Field(
        description="The date of the new match"  
    )
    time: str = Field(
        description="The time of the new match"  
    )
    home: str = Field(
        description="The home team's name of the new match"
    )
    away: str = Field(
        description="The away team's name of the new match"
    )
    home_score: int = Field(
        default=0,
        description="The goal number of home team"
    )
    away_score: int = Field(
        default=0,
        description="The goal number of away team"
    )