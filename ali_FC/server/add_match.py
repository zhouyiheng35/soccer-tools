import os
import json
import uuid

from common.utils.Ch2En import TEAM_NAME_MAP

DATA_DIR = os.environ.get("DATA_DIR", "./test_data")

def add_match(
    league: str,
    date: str,
    time: str,
    home: str,
    away: str,
    home_score: int = 0,
    away_score: int = 0,
) -> str:
    missing = []
    for field_name, field_value in {
        "date": date,
        "time": time,
        "home": home,
        "away": away,
    }.items():
        if field_value is None or str(field_value).strip() == "":
            missing.append(field_name)

    if missing:
        return f"缺少必要字段：{', '.join(missing)}。请补全后重试。"

    home_norm = TEAM_NAME_MAP.get(home, home)
    away_norm = TEAM_NAME_MAP.get(away, away)

    json_path = os.path.join(DATA_DIR, f"{league}.json")

    fthg = int(home_score or 0)
    ftag = int(away_score or 0)

    if fthg > ftag:
        ftr = "H"
    elif fthg == ftag:
        ftr = "D"
    else:
        ftr = "A"

    new_match = {
        "Div": league,
        "Date": date,
        "Time": time,
        "HomeTeam": home_norm,
        "AwayTeam": away_norm,
        "FTHG": fthg,
        "FTAG": ftag,
        "FTR": ftr,
        "HTHG": 0,
        "HTAG": 0,
        "HTR": "",
        "HS": 0,
        "AS": 0,
        "HST": 0,
        "AST": 0,
        "HF": 0,
        "AF": 0,
        "HC": 0,
        "AC": 0,
        "HY": 0,
        "AY": 0,
        "HR": 0,
        "AR": 0,
        "match_id": str(uuid.uuid4()),
    }

    with open(json_path, "r", encoding="utf-8") as f:
        league_data = json.load(f)

    exists = any(
        m["Date"] == date and m["Time"] == time
        and m["HomeTeam"] == home_norm and m["AwayTeam"] == away_norm
        for m in league_data
    )
    if exists:
        return "比赛已存在，未重复添加"

    league_data.append(new_match)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(league_data, f, ensure_ascii=False, indent=2)

    return "添加比赛成功"

def handler(event, context):
    """
    FC Event Function Entry
    event: bytes / str / dict
    """

    # 1. 解析 event
    if isinstance(event, (bytes, bytearray)):
        event = event.decode("utf-8")

    if isinstance(event, str):
        try:
            event = json.loads(event)
        except Exception:
            return {
                "statusCode": 400,
                "body": "Invalid JSON event"
            }

    # 2. 读取参数
    try:
        league = event["league"]
        date = event["date"]
        time = event["time"]
        home = event["home"]
        away = event["away"]
        home_score = event.get("home_score", 0)
        away_score = event.get("away_score", 0)
    except KeyError as e:
        return {
            "statusCode": 400,
            "body": f"Missing field: {e}"
        }

    # 3. 调用业务逻辑
    result = add_match(
        league=league,
        date=date,
        time=time,
        home=home,
        away=away,
        home_score=home_score,
        away_score=away_score,
    )

    # 4. 返回
    return {
        "statusCode": 200,
        "body": result
    }