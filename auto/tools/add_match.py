import os
import json
import uuid
from fc_decorator import fc
import alibabacloud_oss_v2 as oss

from common.utils.Ch2En import TEAM_NAME_MAP

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

    exists = any(
        m["Date"] == date and m["Time"] == time
        and m["HomeTeam"] == home_norm and m["AwayTeam"] == away_norm
        for m in all_data
    )
    if exists:
        return "比赛已存在，未重复添加"

    all_data.append(new_match)

    try:
        client.put_object(
            oss.PutObjectRequest(
                bucket=DATA_BUCKET,
                key=object_key,
                body=json.dumps(all_data, ensure_ascii=False, indent=2).encode("utf-8")
            )
        )
    except Exception as e:
        return f"写回 OSS 失败: {e}"

    return "添加比赛成功"