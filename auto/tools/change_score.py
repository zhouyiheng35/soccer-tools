import os
import json
from fc_decorator import fc
import alibabacloud_oss_v2 as oss

OSS_REGION = os.environ.get("OSS_REGION", "cn-beijing")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT")
OSS_BUCKET = os.environ.get("OSS_BUCKET", "soccer-data")
OSS_PREFIX = os.environ.get("OSS_PREFIX", "leagues")

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
def change_score(
    match: list[dict],
    home_score: int,
    away_score: int,
) -> str:
    if not match or len(match) == 0:
        return "更改失败，没找到比赛。"

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

    object_key = f"{OSS_PREFIX}/{league}.json"

    try:
        resp = client.get_object(
            oss.GetObjectRequest(
                bucket=OSS_BUCKET,
                key=object_key
            )
        )
        all_data = json.loads(resp.body.read().decode("utf-8"))
    except Exception as e:
        return f"读取联赛数据失败: {e}"

    updated = False
    for i, mm in enumerate(all_data):
        if str(mm.get("match_id")) == str(match_id):
            all_data[i] = m
            updated = True
            break

    if not updated:
        return "更改失败，未在联赛数据中找到对应比赛"

    try:
        client.put_object(
            oss.PutObjectRequest(
                bucket=OSS_BUCKET,
                key=object_key,
                body=json.dumps(all_data, ensure_ascii=False, indent=2).encode("utf-8")
            )
        )
    except Exception as e:
        return f"写回 OSS 失败: {e}"

    return "比分更新成功"