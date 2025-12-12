import os
import json
import uuid
import pandas as pd
from datetime import datetime

INPUT_DIR = r"/home/zhouyiheng/langchain_mcp/data"
OUTPUT_DIR = r"/home/zhouyiheng/langchain_mcp/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ODDS_COLUMNS = {
    "B365H", "B365D", "B365A",
    "BWH", "BWD", "BWA",
    "IWH", "IWD", "IWA",
    "LBH", "LBD", "LBA",
    "PSH", "PSD", "PSA",
    "WHH", "WHD", "WHA",
    "VCH", "VCD", "VCA",
    "Bb1X2", "BbMxH", "BbAvH", "BbMxD", "BbAvD", "BbMxA", "BbAvA",
    "BbOU", "BbMx>2.5", "BbAv>2.5", "BbMx<2.5", "BbAv<2.5",
    "GBH", "GBD", "GBA",
    "SBH", "SBD", "SBA"
}

def convert_date_format(date_str):
    """把 dd/mm/yyyy 转成 yyyy-mm-dd"""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return date_str


def process_csv_to_json(csv_path, json_path):
    df = pd.read_csv(csv_path)

    cols_to_drop = [c for c in df.columns if c in ODDS_COLUMNS]

    if "AR" in df.columns:
        ar_idx = df.columns.get_loc("AR")
        cols_to_drop.extend(df.columns[ar_idx + 1:])

    df = df.drop(columns=set(cols_to_drop), errors="ignore")

    records = df.to_dict(orient="records")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    print(f" 转换完成：{os.path.basename(csv_path)} → {json_path}")


def add_match_id(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for match in data:
        if "match_id" not in match:
            match["match_id"] = str(uuid.uuid4())
            changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"添加 match_id：{os.path.basename(filepath)}")
    else:
        print(f"跳过（已有 match_id）：{os.path.basename(filepath)}")


def update_dates(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for match in data:
        if "Date" in match:
            new_date = convert_date_format(match["Date"])
            if new_date != match["Date"]:
                match["Date"] = new_date
                changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"日期已统一格式：{os.path.basename(filepath)}")


def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".csv"):
            csv_path = os.path.join(INPUT_DIR, filename)
            json_path = os.path.join(OUTPUT_DIR, filename.replace(".csv", ".json"))

            process_csv_to_json(csv_path, json_path)

            add_match_id(json_path)

            update_dates(json_path)

    print("\n 所有 CSV 文件已处理完毕！")


if __name__ == "__main__":
    main()
