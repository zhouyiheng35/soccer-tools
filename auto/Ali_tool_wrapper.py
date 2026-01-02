from typing import Type
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

from FC_client import AliFC

class DetectLeagueInput(BaseModel):
    team: str = Field(
        description="Team name, can be in Chinese or English"    
    )

class LoadTeamMatchesInput(BaseModel):
    league: str = Field(
        description="League code, e.g. E0 for Premier League"
    )
    team: str = Field(
        description="Team name"
    )

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

class DeleteMatchesInput(BaseModel):
    matches: list[dict] = Field(
        description="List of match records"
    )


TOOL_INPUT_MODELS: dict[str, Type[BaseModel]] = {
    "detect_league": DetectLeagueInput,
    "load_team_matches": LoadTeamMatchesInput,
    "query_matches": QueryMatchesInput,
    "change_score": ChangeScoreInput,
    "add_match": AddMatchInput,
    "delete_matches": DeleteMatchesInput,
}


def Ali_tool_wrapper(tool_name: str) -> StructuredTool:
    """
    LangChain Tool wrapper
    - tool_name 来自 mytools
    - schema 来自你本地定义的 Pydantic
    - 执行走 FC
    """

    if tool_name not in TOOL_INPUT_MODELS:
        raise ValueError(f"No input schema defined for tool: {tool_name}")

    args_schema = TOOL_INPUT_MODELS[tool_name]

    # lambda 里用 _tool_name 绑定，避免闭包坑
    def _call_fc(**kwargs):
        return AliFC.call_fc_function(
            args={
                "tool": tool_name,
                "args": kwargs
            }
        )

    return StructuredTool.from_function(
        name=tool_name,
        description=f"Call tool `{tool_name}` via Aliyun FC",
        args_schema=args_schema,
        func=_call_fc,
    )