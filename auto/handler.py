import json
import os
import uuid
from typing import List, Dict, Any, Optional, Protocol

import alibabacloud_oss_v2 as oss

OSS_REGION = os.environ.get("OSS_REGION", "cn-beijing")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT")
TOOLS_BUCKET = os.environ.get("TOOLS_BUCKET", "soccer-tools")
DATA_BUCKET = os.environ.get("DATA_BUCKET", "soccer-data")

def create_oss_client():
    cfg = oss.config.load_default()
    cfg.credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    cfg.region = OSS_REGION
    if OSS_ENDPOINT:
        cfg.endpoint = OSS_ENDPOINT if OSS_ENDPOINT.startswith("http") else f"https://{OSS_ENDPOINT}"
    return oss.Client(cfg)

client = create_oss_client()

RUNTIME_GLOBALS = {
    "json": json,
    "oss": oss,
    "client": client,
    "DATA_BUCKET": DATA_BUCKET,
    "List": List,
    "Dict": Dict,
    "Any": Any,
    "Optional": Optional,
    "uuid": uuid
}

def preload_common_deps():
    dep_globals = {
        "Protocol": Protocol,
        "List": List,
        "Dict": Dict,
        "Any": Any,
        "json": json,
        "oss": oss
    }

    def load_py(key: str):
        obj = client.get_object(
            oss.GetObjectRequest(bucket=TOOLS_BUCKET, key=key)
        )
        return obj.body.read().decode("utf-8")

    exec(load_py("common/utils/En2Le.py"), dep_globals)
    exec(load_py("common/utils/Ch2En.py"), dep_globals)
    exec(load_py("common/storage/oss_storage.py"), dep_globals)

    RUNTIME_GLOBALS["TEAM_NAME_MAP"] = dep_globals["TEAM_NAME_MAP"]
    RUNTIME_GLOBALS["TEAM_NAME_MAP1"] = dep_globals["TEAM_NAME_MAP1"]
    
    OSSLeagueStorage = dep_globals["OSSLeagueStorage"]
    storage = OSSLeagueStorage(
        client=client,
        bucket=DATA_BUCKET,
    )
    RUNTIME_GLOBALS["storage"] = storage

preload_common_deps()

_TOOL_CACHE = {}

def load_tool(tool_name: str):
    if tool_name in _TOOL_CACHE:
        return _TOOL_CACHE[tool_name]

    obj = client.get_object(
        oss.GetObjectRequest(
            bucket=TOOLS_BUCKET,
            key=f"tool/{tool_name}.json"
        )
    )
    tool_def = json.loads(obj.body.read())

    locals_dict = {}
    exec(tool_def["source"], RUNTIME_GLOBALS, locals_dict)

    fn = locals_dict[tool_name]
    _TOOL_CACHE[tool_name] = fn
    return fn

def handler(event, context):
    try:
        if isinstance(event, (bytes, bytearray)):
            event = event.decode("utf-8")
        if isinstance(event, str):
            event = json.loads(event)
        
        body = event.get("body") if "body" in event else event
        if isinstance(body, str):
            body = json.loads(body)

        tool_name = body.get("tool")
        args = body.get("args", {})

        if not tool_name:
            return {"statusCode": 400, "body": json.dumps({"error": "missing tool name"})}

        args = body.get("args", {})

        fn = load_tool(tool_name)
        result = fn(**args)

        return {"statusCode": 200, "body": json.dumps({"result": result}, ensure_ascii=False)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}