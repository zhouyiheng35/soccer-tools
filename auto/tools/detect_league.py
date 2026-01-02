from fc_decorator import fc

@fc
def detect_league(team: str) -> str:
    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    league = TEAM_NAME_MAP1[team_en]
    return league
