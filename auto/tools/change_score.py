from fc_decorator import fc

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

    try:
        all_data = storage.load_league(league)
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
        storage.save_league(league, all_data)
    except Exception as e:
        return f"写回 OSS 失败: {e}"

    return "比分更新成功"