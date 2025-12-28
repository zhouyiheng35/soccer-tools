import os
import json

DATA_DIR = os.environ.get("DATA_DIR", "./test_data")

def delete_matches(
    matches: list[dict],
) -> str:
    if not matches or len(matches) == 0:
        return "删除失败，没找到比赛。"

    league = matches[0].get("Div")
    if not league:
        return "删除失败，比赛数据中缺少 Div"

    json_path = os.path.join(DATA_DIR, f"{league}.json")
    if not os.path.exists(json_path):
        return "删除失败，联赛数据文件不存在"

    with open(json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    match_ids_to_delete = {
        str(m.get("match_id"))
        for m in matches
        if m.get("match_id") is not None
    }

    if not match_ids_to_delete:
        return "删除失败，未提供有效的 match_id"

    original_count = len(all_data)

    filtered_data = [
        m for m in all_data
        if str(m.get("match_id")) not in match_ids_to_delete
    ]

    deleted_count = original_count - len(filtered_data)

    if deleted_count == 0:
        return "删除失败，未在数据中找到指定比赛"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    return f"删除成功！删除了 {deleted_count}/{original_count} 场比赛。"

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

    # 2️⃣ 读取参数（严格按你的 MCP 接口）
    try:
        matches = event["matches"]
    except KeyError as e:
        return {
            "statusCode": 400,
            "body": f"Missing field: {e}"
        }

    # 3️⃣ 调用业务逻辑
    result = delete_matches(matches=matches)

    # 4️⃣ 返回
    return {
        "statusCode": 200,
        "body": result
    }