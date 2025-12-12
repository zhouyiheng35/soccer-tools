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
    with open(json_path, encoding="utf-8") as f:
        matches = json.load(f)

    # 最终结果
    result = []

    # 遍历所有比赛
    for m in matches:
        home = m.get("HomeTeam")
        away = m.get("AwayTeam")

        # 如果匹配到队伍
        if home == team_en or away == team_en:
            # 添加到返回结果中
            result.append({
                "Div": m.get("Div"),
                "Date": m.get("Date"),
                "Time": m.get("Time"),
                "HomeTeam": m.get("HomeTeam"),
                "AwayTeam": m.get("AwayTeam"),
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
        matches(List[Dict[str, Any]]): The league code(e.g., 'E0', 'D1', ...) which the team belongs to through 'detect_league' tool.
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

        if date and date_m != date:
            continue

        if home_or_away:
            if home_or_away.lower() == "home" and home != team_en:
                continue
            if home_or_away.lower() == "away" and away != team_en:
                continue

        if result:
            if home == team_en:
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


# @mcp.tool()
# async def add_match(
#     date: Optional[str] = None,
#     time: Optional[str] = None,
#     home: Optional[str] = None,
#     away: Optional[str] = None,
#     home_score: int = 0,
#     away_score: int = 0,
# ) -> Dict[str, Any]:
#     """
#     Add a new match to a league JSON file.

#     Required parameters:
#       - date: YYYY-MM-DD
#       - time: HH:MM
#       - home: home team (Chinese or English)
#       - away: away team (Chinese or English)
#       - home_score: optional
#       - away_score: optional

#     If user want to add a match, you needn't to call the update_score tool.

#     Returns:
#       - {"status": "ok", "match": {...}}
#       - {"status": "error", "message": "..."}
#     """

#     missing = []
#     for field_name, field_value in {
#         "date": date,
#         "time": time,
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
#     league_code2 = TEAM_NAME_MAP1.get(away_norm)

#     if league_code != league_code2:
#         return {
#             "status": "error",
#             "message": f"主队（{home_norm}）与客队（{away_norm}）不属于同一联赛，无法创建比赛。",
#         }

#     json_path = os.path.join(DATA_DIR, f"{league_code}.json")
#     if not os.path.exists(json_path):
#         return {
#             "status": "error",
#             "message": f"未找到联赛：{league_code}。",
#         }

#     fthg = int(home_score or 0)
#     ftag = int(away_score or 0)

#     if fthg > ftag:
#         ftr = "H"
#     elif fthg == ftag:
#         ftr = "D"
#     else:
#         ftr = "A"

#     new_match = {
#         "Div": league_code,
#         "Date": date,
#         "Time": time,
#         "HomeTeam": home_norm,
#         "AwayTeam": away_norm,

#         "FTHG": fthg,
#         "FTAG": ftag,
#         "FTR": ftr,

#         "HTHG": 0,
#         "HTAG": 0,
#         "HTR": "",

#         "HS": 0,
#         "AS": 0,
#         "HST": 0,
#         "AST": 0,
#         "HF": 0,
#         "AF": 0,
#         "HC": 0,
#         "AC": 0,
#         "HY": 0,
#         "AY": 0,
#         "HR": 0,
#         "AR": 0,

#         "match_id": str(uuid.uuid4()),
#     }

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
    
#     league_data.append(new_match)

#     try:
#         save_league(league_code, league_data)
#     except Exception as e:
#         league_data.pop()
#         return {
#             "status": "error",
#             "message": f"保存文件失败：{e}",
#             "exception": str(e),
#         }

#     return {
#         "status": "ok",
#         "message": f"比赛已成功加入 {league_code}",
#         "match": new_match,
#     }


# @mcp.tool()
# async def update_score(
#     home: str | None = None,
#     away: str | None = None,
#     home_score: int | None = None,
#     away_score: int | None = None,
# ):
#     """
#     Update a match's full time score to a league JSON file.

#     Required parameters:
#       - home: home team (Chinese or English)
#       - away: away team (Chinese or English)
#       - home_score: updated home team full time score
#       - away_score: updated away team full time score

#     Returns:
#       - {"status": "ok", "message": {...}}
#       - {"status": "error", "message": "..."}
#     """
#     missing = []
#     for field_name, field_value in {
#         "home": home,
#         "away": away,
#         "home_score": home_score,
#         "away_score": away_score,
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
    
#     match_found = None
#     for match in league_data:
#         if match.get("HomeTeam") == home_norm and match.get("AwayTeam") == away_norm:
#             match_found = match
#             break
    
#     if not match_found:
#         return {
#             "status": "error",
#             "message": f"未找到比赛：{home_norm} vs {away_norm}",
#         }
    
#     fthg = home_score
#     ftag = away_score

#     match_found["FTHG"] = fthg
#     match_found["FTAG"] = ftag

#     match_found["FTR"] = (
#         "H" if fthg > ftag else
#         "A" if fthg < ftag else
#         "D"
#     )

#     try:
#         save_league(league_code, league_data)
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"保存文件失败：{e}",
#         }

#     return {
#         "status": "ok",
#         "message": "比赛已成功更新",
#         "league": league_code,
#         "updated_match": match_found,
#     }


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


# @mcp.tool()
# async def delete_matches(
#     team: Optional[str] = None,
#     date: Optional[str] = None,
#     result: Optional[str] = None,
#     opponent: Optional[str] = None,
#     home_or_away: Optional[str] = None,
# ) -> Dict[str, Any]:
#     """
#     Batch delete matches based on filter conditions.
    
#     Filters:
#     - team: target team (Chinese or English)
#     - date: match date
#     - result: 'win' | 'lose' | 'draw'
#     - opponent: opponent team
#     - home_or_away: 'home' | 'away'

#     If user only tell you the home team and away team, call delete_one_match tool.

#     Returns a report with:
#     - deleted_count
#     - deleted_matches
#     - remaining_matches
#     """

#     if not team:
#         return {"status": "error", "message": "必须指定 team 才能执行删除操作。"}

#     team_en = TEAM_NAME_MAP.get(team, team)

#     if team_en not in TEAM_NAME_MAP1:
#         return {"status": "error", "message": f"未找到球队所属联赛：{team}"}

#     league = TEAM_NAME_MAP1[team_en]
#     json_path = os.path.join(DATA_DIR, f"{league}.json")

#     try:
#         with open(json_path, encoding="utf-8") as f:
#             matches = json.load(f)
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"读取联赛文件失败：{e}",
#             "exception": str(e),
#         }

#     remaining = []
#     deleted = []

#     opp_en = None
#     if opponent:
#         opp_en = TEAM_NAME_MAP.get(opponent, opponent)

#     for m in matches:
#         home = m.get("HomeTeam")
#         away = m.get("AwayTeam")

#         match_team_related = (home == team_en or away == team_en)

#         if not match_team_related:
#             remaining.append(m)
#             continue

#         should_delete = True

#         if date and m.get("Date") != date:
#             should_delete = False

#         if should_delete and home_or_away:
#             if home_or_away.lower() == "home" and home != team_en:
#                 should_delete = False
#             if home_or_away.lower() == "away" and away != team_en:
#                 should_delete = False

#         if should_delete and opp_en:
#             if home == team_en and away != opp_en:
#                 should_delete = False
#             if away == team_en and home != opp_en:
#                 should_delete = False

#         if should_delete and result:
#             ftr = m.get("FTR")
#             team_is_home = (home == team_en)

#             if result == "win":
#                 if (team_is_home and ftr != "H") or (not team_is_home and ftr != "A"):
#                     should_delete = False
#             elif result == "lose":
#                 if (team_is_home and ftr != "A") or (not team_is_home and ftr != "H"):
#                     should_delete = False
#             elif result == "draw":
#                 if ftr != "D":
#                     should_delete = False

#         if should_delete:
#             deleted.append(m)
#         else:
#             remaining.append(m)

#     if not deleted:
#         return {
#             "status": "ok",
#             "deleted_count": 0,
#             "message": "没有任何匹配的比赛被删除。",
#             "filters": {
#                 "team": team,
#                 "date": date,
#                 "result": result,
#                 "opponent": opponent,
#                 "home_or_away": home_or_away,
#             }
#         }

#     try:
#         save_league(league, remaining)
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"写回文件失败：{e}",
#             "exception": str(e),
#         }

#     return {
#         "status": "ok",
#         "message": f"成功删除 {len(deleted)} 场比赛",
#         "deleted_count": len(deleted),
#         "deleted_matches": deleted,
#         "remaining_matches": len(remaining),
#     }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")