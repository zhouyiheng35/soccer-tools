import os
import json

from common.utils.Ch2En import TEAM_NAME_MAP

DATA_DIR = os.environ.get("DATA_DIR", "./test_data")


def load_team_matches(
    league: str,
    team: str
) -> list[dict]:
    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    json_path = os.path.join(DATA_DIR, f"{league}.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"league data not found: {league}")

    with open(json_path, "r", encoding="utf-8") as f:
        matches = json.load(f)

    result = []

    for m in matches:
        home = m.get("HomeTeam")
        away = m.get("AwayTeam")

        if home in TEAM_NAME_MAP:
            home_norm = TEAM_NAME_MAP[home]
        else:
            home_norm = home

        if away in TEAM_NAME_MAP:
            away_norm = TEAM_NAME_MAP[away]
        else:
            away_norm = away

        if home_norm == team_en or away_norm == team_en:
            result.append({
                "Div": m.get("Div"),
                "Date": m.get("Date"),
                "Time": m.get("Time"),
                "HomeTeam": home_norm,
                "AwayTeam": away_norm,
                "FTHG": m.get("FTHG"),
                "FTAG": m.get("FTAG"),
                "FTR": m.get("FTR"),
                "HTHG": m.get("HTHG"),
                "HTAG": m.get("HTAG"),
                "HTR": m.get("HTR"),
                "HS": m.get("HS"),
                "AS": m.get("AS"),
                "HST": m.get("HST"),
                "AST": m.get("AST"),
                "HF": m.get("HF"),
                "AF": m.get("AF"),
                "HC": m.get("HC"),
                "AC": m.get("AC"),
                "HY": m.get("HY"),
                "AY": m.get("AY"),
                "HR": m.get("HR"),
                "AR": m.get("AR"),
                "match_id": m.get("match_id")
            })

    return result


def handler(event, context):
    try:
        # event 是 bytes
        if isinstance(event, (bytes, bytearray)):
            body = json.loads(event.decode("utf-8") or "{}")
        else:
            body = event or {}

        league = body.get("league")
        team = body.get("team")

        if not league or not team:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "missing required params: league, team"},
                    ensure_ascii=False
                )
            }

        matches = load_team_matches(league, team)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"matches": matches},
                ensure_ascii=False
            )
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": str(e)},
                ensure_ascii=False
            )
        }
