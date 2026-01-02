from fc_decorator import fc

@fc
def load_team_matches(league: str, team: str) -> list[dict]:
    team_en = TEAM_NAME_MAP.get(team, team)
    matches = storage.load_league(league)

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
