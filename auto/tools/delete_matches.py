import os
import json
from fc_decorator import fc
import alibabacloud_oss_v2 as oss

OSS_REGION = os.environ.get("OSS_REGION", "cn-beijing")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT")
DATA_BUCKET = os.environ.get("DATA_BUCKET", "soccer-data")

def create_oss_client():
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = OSS_REGION
    if OSS_ENDPOINT:
        cfg.endpoint = OSS_ENDPOINT if OSS_ENDPOINT.startswith("http") else f"https://{OSS_ENDPOINT}"
    return oss.Client(cfg)

client = create_oss_client()

@fc
def delete_matches(
    matches: list[dict],
) -> str:
    if not matches or len(matches) == 0:
        return "删除失败，没找到比赛。"

    league = matches[0].get("Div")
    if not league:
        return "删除失败，比赛数据中缺少 Div"

    object_key = f"leagues/{league}.json"
    try:
        resp = client.get_object(
            oss.GetObjectRequest(
                bucket=DATA_BUCKET,
                key=object_key
            )
        )
        all_data = json.loads(resp.body.read().decode("utf-8"))
    except Exception as e:
        return f"读取联赛数据失败: {e}"

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

    try:
        client.put_object(
            oss.PutObjectRequest(
                bucket=DATA_BUCKET,
                key=object_key,
                body=json.dumps(filtered_data, ensure_ascii=False, indent=2).encode("utf-8")
            )
        )
    except Exception as e:
        return f"写回 OSS 失败: {e}"

    return f"删除成功！删除了 {deleted_count}/{original_count} 场比赛。"