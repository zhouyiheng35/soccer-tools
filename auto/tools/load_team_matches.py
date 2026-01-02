import os
import json
from fc_decorator import fc
import alibabacloud_oss_v2 as oss
# from common.utils.Ch2En import TEAM_NAME_MAP

# ================= OSS 配置 =================
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
def load_team_matches(league: str, team: str) -> list[dict]:
    team_en = TEAM_NAME_MAP.get(team, team)
    object_key = f"leagues/{league}.json"

    response = client.get_object(oss.GetObjectRequest(bucket=DATA_BUCKET, key=object_key))
    with response.body as stream:
        body_bytes = stream.read()
    matches = json.loads(body_bytes.decode("utf-8"))

    result = []
    for m in matches:
        home = TEAM_NAME_MAP.get(m.get("HomeTeam"), m.get("HomeTeam"))
        away = TEAM_NAME_MAP.get(m.get("AwayTeam"), m.get("AwayTeam"))
        if home == team_en or away == team_en:
            result.append({
                "Div": m.get("Div"),
                "Date": m.get("Date"),
                "Time": m.get("Time"),
                "HomeTeam": home,
                "AwayTeam": away,
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
