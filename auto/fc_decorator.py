import json
import inspect
import textwrap

import alibabacloud_oss_v2 as oss

def strip_decorators(func):
    src = inspect.getsource(func)
    lines = src.splitlines()
    while lines[0].lstrip().startswith("@"):
        lines.pop(0)
    return textwrap.dedent("\n".join(lines))

def fc(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    source_code = strip_decorators(func)
    tool_def = {
        "name": func.__name__,
        "type": "python_function",
        "signature": str(inspect.signature(func)),
        "source": source_code,
        "runtime": "python3.10"
    }

    cfg = oss.config.load_default()
    cfg.region = "cn-beijing"
    cfg.credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    client = oss.Client(cfg)

    client.put_object(
        oss.PutObjectRequest(
            bucket="soccer-tools",
            key=f"tool/{func.__name__}.json",
            body=json.dumps(tool_def, ensure_ascii=False).encode("utf-8")
        )
    )

    return wrapper