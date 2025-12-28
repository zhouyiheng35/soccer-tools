import os
import json

DATA_DIR = os.environ.get("DATA_DIR", "./test_data")

def change_score(
    match: list[dict],
    home_score: int,
    away_score: int,
) -> str:
    if not match or len(match) == 0:
        return "更改失败，没找到比赛。"

    # 你原来的逻辑：只改第一场
    m = match[0]

    fthg = int(home_score)
    ftag = int(away_score)

    m["FTHG"] = fthg
    m["FTAG"] = ftag
    m["FTR"] = (
        "H" if fthg > ftag else
        "A" if fthg < ftag else
        "D"
    )

    league = m.get("Div")
    match_id = m.get("match_id")

    if not league or not match_id:
        return "比赛数据不完整，缺少 Div 或 match_id"

    path = os.path.join(DATA_DIR, f"{league}.json")

    if not os.path.exists(path):
        return "联赛数据文件不存在"

    with open(path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    updated = False
    for i, mm in enumerate(all_data):
        if str(mm.get("match_id")) == str(match_id):
            all_data[i] = m
            updated = True
            break

    if not updated:
        return "更改失败，未在文件中找到对应比赛"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    return "比分更新成功"


def handler(event, context):
    """
    FC Event Function Entry
    """

    # 1️⃣ 解析 event
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

    # 2️⃣ 读取参数（严格按你的接口）
    try:
        match = event["match"]
        home_score = event["home_score"]
        away_score = event["away_score"]
    except KeyError as e:
        return {
            "statusCode": 400,
            "body": f"Missing field: {e}"
        }

    # 3️⃣ 调用业务逻辑
    result = change_score(
        match=match,
        home_score=home_score,
        away_score=away_score,
    )

    # 4️⃣ 返回
    return {
        "statusCode": 200,
        "body": result
    }
