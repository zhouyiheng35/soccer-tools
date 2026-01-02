from fc_decorator import fc

@fc
def query_matches(
    matches: List[Dict[str, Any]],
    team: str,
    date: Optional[str]=None,
    result: Optional[str]=None,
    home_or_away: Optional[str]=None
) -> list[dict]:
    """核心逻辑保持不变"""
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
            team_is_home = (home_norm == team_en)
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