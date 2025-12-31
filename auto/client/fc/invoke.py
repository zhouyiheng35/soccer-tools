import json
from alibabacloud_darabonba_stream.client import Client as StreamClient
from alibabacloud_fc20230330 import models as fc_models
from alibabacloud_tea_util import models as util_models
from .client import get_fc_client

def call_fc_function(function_name: str, args: dict) -> dict:
        client = get_fc_client()
        payload = {
            "tool": function_name,
            "args": args
        }
        body_stream = StreamClient.read_from_string(
            json.dumps(payload, ensure_ascii=False)
        )
        headers = fc_models.InvokeFunctionHeaders(
            x_fc_invocation_type='Sync',
            x_fc_log_type='None'
        )
        request = fc_models.InvokeFunctionRequest(
            qualifier='LATEST',
            body=body_stream
        )
        runtime = util_models.RuntimeOptions()

        resp = client.invoke_function_with_options("oss_test", request, headers, runtime)
        raw = resp.body.read().decode("utf-8")
        try:
            data = json.loads(raw)

            # FC 标准返回
            if isinstance(data, dict) and "body" in data:
                body = data["body"]

                # body 本身是 JSON 字符串
                if isinstance(body, str):
                    try:
                        return json.loads(body)
                    except json.JSONDecodeError:
                        # body 就是普通字符串，比如“比分更新成功”
                        return body

                # body 已经是 dict
                return body

            return data

        except json.JSONDecodeError:
            # FC 直接返回了纯文本
            return raw
        
def list_tools():
    raw = call_fc_function("list_tools", {})
    return raw.get("tools", [])
