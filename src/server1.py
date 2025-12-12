import os
import json
import uuid
from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from common.utils.En2Le import TEAM_NAME_MAP1
from common.utils.Ch2En import TEAM_NAME_MAP, LEAGUE_NAME_MAP

DATA_DIR = "test_data"
mcp = FastMCP("Soccer")

def save_league(league: str, data: list):
    """Wirte back the JSON file."""
    path = os.path.join(DATA_DIR, f"{league}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_league(league: str) -> list:
    """Load the JSON file."""
    path = os.path.join(DATA_DIR, f"{league}.json")
    if not os.path.exists(path):
        raise Exception(f"联赛 {league} 不存在（{path} 文件找不到）")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
    

@mcp.tool()
async def detect_league(team: str) -> str:
    """
    Analyze which league the team belongs to based on the team name.

    Args:
        team(str): The name of the team.

    Returns:
        str: A league that the team belongs to(e.g., 'E0', 'D1', ...).
    """
    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    league = TEAM_NAME_MAP1[team_en]
    print("DEBUG league:", league)
    return league


@mcp.tool()
async def load_team_matches(league: str, team: str) -> List[Dict[str, Any]]:
    """
    Load and return all match information of the team in the corresponding league.
    You can't guess the corresponding league by yourself.
    The corresponding league must be found through 'detect_league' tool.

    Args:
        league(str): The league code(e.g., 'E0', 'D1', ...) which the team belongs to through 'detect_league' tool.
        team(str): The name of the team.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing basic information of each matches.
        Each dictionary contains keys:
            - Div (str): The code of league.
            - Date (str): The date of match.
            - Time (str): The time of match.
            - HomeTeam (str): The name of home team.
            - AwayTeam (str): The name of away team.
            - FTHG (int): The number of home team's goals in the full time.
            - FTAG (int): The number of away team's goals in the full time.
            - FTR (int): The result of the full time.
            - HTHG (int): The number of home team's goals in the half time.
            - HTAG (int): The number of away team's goals in the half time.
            - HTR (int): The result of the half time.
            - HS (int): The number of home team's shots in the full time.
            - AS (int): The number of away team's shots in the full time.
            - HST (int): The number of home team's shots on target in the full time.
            - AST (int): The number of away team's shots on target in the full time.
            - HF (int): The number of home team's fouls in the full time.
            - AF (int): The number of away team's fouls in the full time.
            - HC (int): The number of home team's corners in the full time.
            - AC (int): The number of away team's corners in the full time.
            - HY (int): The number of home team's yellow cards in the full time.
            - AY (int): The number of away team's yellow cards in the full time.
            - HR (int): The number of home team's red cards in the full time.
            - AR (int): The number of away team's red cards in the full time.
            - match_id (str): The ID of match.
    """
    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    json_path = os.path.join(DATA_DIR, f"{league}.json")
    with open(json_path, "r", encoding="utf-8") as f:
        matches = json.load(f)

    # 最终结果
    result = []

    # 遍历所有比赛
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

        # 如果匹配到队伍
        if home_norm == team_en or away_norm == team_en:
            # 添加到返回结果中
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


@mcp.tool()
async def query_matches(
    matches: List[Dict[str, Any]],
    team: str, 
    date: str | None = None,
    result: str | None = None,
    home_or_away: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Filter matches that meet the criteria according to the specified rules.

    Args:
        matches(List[Dict[str, Any]]): A list of potential matches.
        team(str): The name of team.
        date(str): The date of match.
        result(str): The result of the team. It shouble be transformed to 'win', 'draw' or 'lose'.
        home_or_away(str): The team is home or away. It shouble be transformed to 'home' or 'away'.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing basic information of each matches.
        Each dictionary contains keys:
            - Div (str): The code of league.
            - Date (str): The date of match.
            - Time (str): The time of match.
            - HomeTeam (str): The name of home team.
            - AwayTeam (str): The name of away team.
            - FTHG (int): The number of home team's goals in the full time.
            - FTAG (int): The number of away team's goals in the full time.
            - FTR (int): The result of the full time.
            - HTHG (int): The number of home team's goals in the half time.
            - HTAG (int): The number of away team's goals in the half time.
            - HTR (int): The result of the half time.
            - HS (int): The number of home team's shots in the full time.
            - AS (int): The number of away team's shots in the full time.
            - HST (int): The number of home team's shots on target in the full time.
            - AST (int): The number of away team's shots on target in the full time.
            - HF (int): The number of home team's fouls in the full time.
            - AF (int): The number of away team's fouls in the full time.
            - HC (int): The number of home team's corners in the full time.
            - AC (int): The number of away team's corners in the full time.
            - HY (int): The number of home team's yellow cards in the full time.
            - AY (int): The number of away team's yellow cards in the full time.
            - HR (int): The number of home team's red cards in the full time.
            - AR (int): The number of away team's red cards in the full time.
            - match_id (str): The ID of match.
    """
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
            if home_norm == team_en:
                team_is_home = True
            else:
                team_is_home = False

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


@mcp.tool()
async def add_match(
    league: str,
    date: str,
    time: str,
    home: str,
    away: str,
    home_score: int = 0,
    away_score: int = 0,
) -> str:
    """
    Add a new match.
    When calling this tool, if any field(date, time, home, away) is missing, 
    you must refuse and ask for clarification.

    Args:
        league(str): The league code(e.g., 'E0', 'D1', ...) which the team belongs to through 'detect_league' tool.
        date(str): The date of the new match.
        time(str): The time of the new match.
        home(str): The home team's name of the new match.
        away(str): The away team's name of the new match.
        home_score(int): Goals scored by the home team after the change.
        away_score(int): Goals scored by the away team after the change.

    Returns:
        str: A string used to indicate whether the action was successful or failed.
    """
    print(f"调用 add_match: {home} vs {away} 日期: {date} {time}")
    missing = []
    for field_name, field_value in {
        "date": date,
        "time": time,
        "home": home,
        "away": away,
    }.items():
        if field_value is None or field_value.strip() == "":
            missing.append(field_name)

    if missing:
        return f"缺少必要字段：{', '.join(missing)}。请补全后重试。"
    
    if home in TEAM_NAME_MAP:
        home_norm = TEAM_NAME_MAP[home]
    else:
        home_norm = home

    if away in TEAM_NAME_MAP:
        away_norm = TEAM_NAME_MAP[away]
    else:
        away_norm = away

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

    # 检查是否已有相同比赛
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


@mcp.tool()
async def change_score(
    match: List[Dict[str, Any]],
    home_score: int,
    away_score: int,
) -> str:
    """
    Change a match's full time score and result.

    Args:
        matches(List[Dict[str, Any]]): A list of potential matches.
        home_score(int): Goals scored by the home team after the change.
        away_score(int): Goals scored by the away team after the change.

    Returns:
        str: A string used to indicate whether the change was successful or failed.
    """
    if len(match) == 0:
        return "更改失败，没找到比赛。"
    
    m = match[0]
    
    fthg = home_score
    ftag = away_score

    m["FTHG"] = fthg
    m["FTAG"] = ftag

    m["FTR"] = (
        "H" if fthg > ftag else
        "A" if fthg < ftag else
        "D"
    )

    league = m.get("Div")
    id = m.get("match_id")

    path = os.path.join(DATA_DIR, f"{league}.json")
    with open(path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    for i, mm in enumerate(all_data):
        if mm.get("match_id") == id:
            all_data[i] = m
            break

    with open(path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    return "比分更新成功"


# @mcp.tool()
# async def delete_one_match(
#     home: str | None = None,
#     away: str | None = None,
# ):
#     """
#     Delete an existing match from its league JSON file.

#     Required parameters:
#       - home: home team (Chinese or English)
#       - away: away team (Chinese or English)

#     If user only tell you the home team and away team, call this tool.

#     Returns:
#       - {"status": "ok", "message": {...}}
#       - {"status": "error", "message": "..."}
#     """
#     missing = []
#     for field_name, field_value in {
#         "home": home,
#         "away": away,
#     }.items():
#         if field_value is None:
#             missing.append(field_name)

#     if missing:
#         return {
#             "status": "error",
#             "message": f"缺少必要字段：{', '.join(missing)}。请补全后重试。",
#             "missing": missing,
#         }

#     home_norm = TEAM_NAME_MAP.get(home, home)
#     away_norm = TEAM_NAME_MAP.get(away, away)

#     league_code = TEAM_NAME_MAP1.get(home_norm)

#     if not league_code:
#         return {
#             "status": "error",
#             "message": f"无法根据主队 '{home}' 推断所属联赛，请确认队名是否正确。",
#         }

#     json_path = os.path.join(DATA_DIR, f"{league_code}.json")
#     if not os.path.exists(json_path):
#         return {
#             "status": "error",
#             "message": f"未找到联赛：{league_code}。",
#         }
    
#     try:
#         league_data = load_league(league_code)
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"加载联赛文件失败：{e}",
#             "exception": str(e)
#         }

#     if not isinstance(league_data, list):
#         return {
#             "status": "error",
#             "message": f"{league_code}.json 格式错误，必须是 list。",
#         }
    
#     before = len(league_data)
#     league_data = [
#         m for m in league_data
#         if not (m["HomeTeam"] == home_norm and 
#                 m["AwayTeam"] == away_norm)
#     ]

#     if len(league_data) == before:
#         return {
#             "status": "error",
#             "message": f"比赛不存在，无法删除",
#             "league": league_code,
#         }

#     try:
#         save_league(league_code, league_data)
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"保存文件失败：{e}",
#             "exception": str(e),
#         }

#     return {
#         "status": "ok",
#         "message": f"比赛已成功删除",
#         "league": league_code,
#     }


@mcp.tool()
async def delete_matches(
    matches: List[Dict[str, Any]],
) -> str:
    """
    Delete all the matches in the given arg.

    Args:
        matches(List[Dict[str, Any]]): A list of matches that should be deleted.

    Return:
        str: A string used to indicate whether the delete was successful or failed.
    """

    if len(matches) == 0:
        return "删除失败，没找到比赛。"
    
    league = matches[0].get("Div")
    json_path = os.path.join(DATA_DIR, f"{league}.json")
    with open(json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    match_ids_to_delete = set()
    for match in matches:
        id = match.get("match_id")
        match_ids_to_delete.add(str(id))

    original_count = len(all_data)
    filtered_data = []
    deleted_count = 0

    for match in all_data:
        id = str(match.get("match_id", ""))
        if id not in match_ids_to_delete:
            filtered_data.append(match)

    deleted_count = original_count - len(filtered_data)
    if deleted_count == 0:
        return "删除失败，未在数据中找到指定比赛"
    
    with open(json_path, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    return f"删除成功！删除了 {deleted_count}/{original_count} 场比赛。"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")