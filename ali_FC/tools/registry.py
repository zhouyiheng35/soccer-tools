from langchain_core.tools import StructuredTool
from models.detect_league import DetectLeagueInput
from models.load_team_matches import LoadTeamMatchesInput
from models.query_matches import QueryMatchesInput
from models.change_score import ChangeScoreInput
from models.add_match import AddMatchInput
from models.delete_matches import DeleteMatchesInput
from fc.invoke import list_tools
from .wrappers import make_tool_func

SCHEMA_MAP = {
    "detect_league": DetectLeagueInput,
    "load_team_matches": LoadTeamMatchesInput,
    "query_matches": QueryMatchesInput,
    "change_score": ChangeScoreInput,
    "add_match": AddMatchInput,
    "delete_matches": DeleteMatchesInput,
}

def build_tools():
    tools = []

    for t in list_tools():
        name = t["name"]
        args_schema = SCHEMA_MAP.get(name)

        tools.append(
            StructuredTool.from_function(
                name=name,
                description=t.get("description", ""),
                func=make_tool_func(name),
                args_schema=args_schema  
            )
        )
    return tools