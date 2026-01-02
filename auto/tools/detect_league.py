from fc_decorator import fc
from common.utils.En2Le import TEAM_NAME_MAP1
from common.utils.Ch2En import TEAM_NAME_MAP

@fc
def detect_league(team: str) -> str:
    if team in TEAM_NAME_MAP:
        team_en = TEAM_NAME_MAP[team]
    else:
        team_en = team

    league = TEAM_NAME_MAP1[team_en]
    return league
