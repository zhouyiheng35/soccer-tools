import json
from fc_decorator import fc

@fc
def list_tools():
    """
    返回所有工具的名字和调用 schema
    """
    tools = [
        {
            "name": "detect_league",
            "description": "Analyze which league the team belongs to based on the team name. Returns a league code such as 'E0' or 'D1'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "The name of the football team"
                    }
                },
                "required": ["team"]
            }
        },
        {
            "name": "load_team_matches",
            "description": "Load all match information of the team in the corresponding league. The league must be obtained through detect_league first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {
                        "type": "string",
                        "description": "League code such as 'E0', 'D1'"
                    },
                    "team": {
                        "type": "string",
                        "description": "The name of the football team"
                    }
                },
                "required": ["league", "team"]
            }
        },
        {
            "name": "query_matches",
            "description": "Filter matches according to date, result, and whether the team is home or away.",
            "parameters": {
                "type": "object",
                "properties": {
                    "matches": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "A list of matches returned by load_team_matches"
                    },
                    "team": {"type": "string"},
                    "date": {"type": "string"},
                    "result": {"type": "string"},
                    "home_or_away": {"type": "string"}
                },
                "required": ["matches", "team"]
            }
        },
        {
            "name": "add_match",
            "description": "Add a new match to the league data. All fields except scores are required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {
                        "type": "string",
                        "description": "League code such as 'E0', 'D1'"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of the match"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time of the match"
                    },
                    "home": {
                        "type": "string",
                        "description": "Home team name"
                    },
                    "away": {
                        "type": "string",
                        "description": "Away team name"
                    },
                    "home_score": {
                        "type": "integer",
                        "description": "Goals scored by the home team"
                    },
                    "away_score": {
                        "type": "integer",
                        "description": "Goals scored by the away team"
                    }
                },
                "required": ["league", "date", "time", "home", "away"]
            }
        },
        {
            "name": "change_score",
            "description": "Change the full time score and result of a match.",
            "parameters": {
                "type": "object",
                "properties": {
                    "match": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "A list containing the match to be modified (from query_matches)"
                    },
                    "home_score": {
                        "type": "integer",
                        "description": "New home team score"
                    },
                    "away_score": {
                        "type": "integer",
                        "description": "New away team score"
                    }
                },
                "required": ["match", "home_score", "away_score"]
            }
        },
        {
            "name": "delete_matches",
            "description": "Delete all matches in the given list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "matches": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Matches to be deleted (from query_matches)"
                    }
                },
                "required": ["matches"]
            }
        }
    ]

    # 返回字典形式，Agent 可以直接使用
    return {
        "tool_names": [t["name"] for t in tools],  # 方便快速拿名字
        "tools": tools  # 完整 schema
    }
