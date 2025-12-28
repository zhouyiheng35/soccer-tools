import json
from typing import List, Dict, Any, Optional
from common.utils.En2Le import TEAM_NAME_MAP1
from common.utils.Ch2En import TEAM_NAME_MAP, LEAGUE_NAME_MAP

def query_matches(
    matches: List[Dict[str, Any]],
    team: str,
    date: Optional[str]=None,
    result: Optional[str]=None,
    home_or_away: Optional[str]=None
) -> list[dict]:
    """核心逻辑保持不变"""
    filtered = []

    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    for m in matches:
        home = m.get("HomeTeam")
        away = m.get("AwayTeam")
        date_m = m.get("Date")
        ftr = m.get("FTR")

        if home in TEAM_NAME_MAP:
            home_norm = TEAM_NAME_MAP[home]
        else:
            home_norm = home

        if away in TEAM_NAME_MAP:
            away_norm = TEAM_NAME_MAP[away]
        else:
            away_norm = away

        if date and date_m != date:
            continue

        if home_or_away:
            if home_or_away.lower() == "home" and home_norm != team_en:
                continue
            if home_or_away.lower() == "away" and away_norm != team_en:
                continue

        if result:
            team_is_home = (home_norm == team_en)
            if result == "win":
                if (team_is_home and ftr != "H") or (not team_is_home and ftr != "A"):
                    continue
            elif result == "lose":
                if (team_is_home and ftr != "A") or (not team_is_home and ftr != "H"):
                    continue
            elif result == "draw":
                if ftr != "D":
                    continue

        filtered.append(m)

    return filtered

def handler(event, context):
    """FC 事件函数入口"""
    try:
        # event 类型是 bytes，需要先 decode
        body_bytes = event if isinstance(event, bytes) else event.get("body", b"")
        body_str = body_bytes.decode("utf-8") if isinstance(body_bytes, bytes) else body_bytes
        body = json.loads(body_str)

        matches = body.get("matches")
        team = body.get("team")
        date = body.get("date")
        result = body.get("result")
        home_or_away = body.get("home_or_away")

        if matches is None or team is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "missing required parameters: matches and team"}, ensure_ascii=False)
            }

        filtered = query_matches(matches, team, date, result, home_or_away)

        return {
            "statusCode": 200,
            "body": json.dumps({"matches": filtered}, ensure_ascii=False)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }
