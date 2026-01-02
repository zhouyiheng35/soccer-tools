import json
import inspect
import alibabacloud_oss_v2 as oss
import textwrap

def strip_decorators(func):
    src = inspect.getsource(func)
    lines = src.splitlines()
    while lines[0].lstrip().startswith("@"):
        lines.pop(0)
    return textwrap.dedent("\n".join(lines))

def fc(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # ===== 1. 提取函数信息 =====
    source_code = strip_decorators(func)
    tool_def = {
        "name": func.__name__,
        "type": "python_function",
        "signature": str(inspect.signature(func)),
        "source": source_code,
        "runtime": "python3.10"
    }

    # ===== 2. 初始化 OSS 客户端 =====
    cfg = oss.config.load_default()
    cfg.region = "cn-beijing"
    cfg.credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    client = oss.Client(cfg)

    # ===== 3. 上传到 OSS =====
    client.put_object(
        oss.PutObjectRequest(
            bucket="soccer-tools",
            key=f"tool/{func.__name__}.json",
            body=json.dumps(tool_def, ensure_ascii=False).encode("utf-8")
        )
    )

    return wrapper
