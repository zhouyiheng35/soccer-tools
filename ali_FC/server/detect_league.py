import json
from common.utils.En2Le import TEAM_NAME_MAP1
from common.utils.Ch2En import TEAM_NAME_MAP, LEAGUE_NAME_MAP

def detect_league(
    team: str
) -> str:
    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    league = TEAM_NAME_MAP1[team_en]
    return league

def handler(event, context):
    try:
        if isinstance(event, bytes):
            event = event.decode("utf-8")

        if isinstance(event, str):
            event = json.loads(event)

        body = None
        if isinstance(event, dict):
            raw_body = event.get("body")
            if raw_body is not None:
                if isinstance(raw_body, bytes):
                    raw_body = raw_body.decode("utf-8")
                if isinstance(raw_body, str):
                    body = json.loads(raw_body)
                elif isinstance(raw_body, dict):
                    body = raw_body
            else:
                body = event

        if not isinstance(body, dict):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "invalid input format"})
            }

        team = body.get("team")
        if not team:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "missing required param: team"})
            }

        league = detect_league(team)

        return {
            "statusCode": 200,
            "body": json.dumps({"league": league}, ensure_ascii=False)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }