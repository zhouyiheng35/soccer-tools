from fc_decorator import fc

@fc
def delete_matches(
    matches: list[dict],
) -> str:
    if not matches or len(matches) == 0:
        return "删除失败，没找到比赛。"

    league = matches[0].get("Div")
    if not league:
        return "删除失败，比赛数据中缺少 Div"

    try:
        all_data = storage.load_league(league)
    except Exception as e:
        return f"读取联赛数据失败: {e}"

    match_ids_to_delete = {
        str(m.get("match_id"))
        for m in matches
        if m.get("match_id") is not None
    }

    if not match_ids_to_delete:
        return "删除失败，未提供有效的 match_id"

    original_count = len(all_data)

    filtered_data = [
        m for m in all_data
        if str(m.get("match_id")) not in match_ids_to_delete
    ]

    deleted_count = original_count - len(filtered_data)

    if deleted_count == 0:
        return "删除失败，未在数据中找到指定比赛"

    try:
        storage.save_league(league, filtered_data)
    except Exception as e:
        return f"写回 OSS 失败: {e}"

    return f"删除成功！删除了 {deleted_count}/{original_count} 场比赛。"