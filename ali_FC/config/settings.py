import os
from dotenv import load_dotenv

# 只在这里 load
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")
BASE_URL = os.getenv("BASE_URL")

FC_ACCESS_KEY_ID = os.getenv("FC_ACCESS_KEY_ID")
FC_ACCESS_KEY_SECRET = os.getenv("FC_ACCESS_KEY_SECRET")

FC_ACCOUNT_ID = os.getenv("FC_ACCOUNT_ID")
FC_REGION = os.getenv("FC_REGION")

def check_required():
    missing = []
    for k in [
        "OPENAI_API_KEY",
        "MODEL",
        "BASE_URL",
        "FC_ACCESS_KEY_ID",
        "FC_ACCESS_KEY_SECRET",
        "FC_ACCOUNT_ID",
        "FC_REGION"
    ]:
        if not os.getenv(k):
            missing.append(k)
    if missing:
        raise RuntimeError(f"Missing env vars: {missing}")