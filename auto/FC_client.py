import os
import json
from dotenv import load_dotenv

from alibabacloud_fc20230330.client import Client as FC20230330Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_darabonba_stream.client import Client as StreamClient
from alibabacloud_fc20230330 import models as fc20230330_models
from alibabacloud_tea_util import models as util_models

load_dotenv()

class AliFC:
    _client = None

    @staticmethod
    def create_client() -> FC20230330Client:
        if AliFC._client is None:
            credential = CredentialClient(
                CredConfig(
                    type="access_key",
                    access_key_id=os.environ["FC_ACCESS_KEY_ID"],
                    access_key_secret=os.environ["FC_ACCESS_KEY_SECRET"],  
                )    
            )
            AliFC._client = FC20230330Client(
                open_api_models.Config(
                    credential=credential,
                    endpoint="1064398619921513.cn-hangzhou.fc.aliyuncs.com",
                )
            )
        return AliFC._client
    
    def call_fc_function(args: dict) -> dict:
        client = AliFC._client or AliFC.create_client()
        body_json_str = json.dumps(args, ensure_ascii=False)
        body_stream = StreamClient.read_from_string(body_json_str)
        headers = fc20230330_models.InvokeFunctionHeaders(
            x_fc_invocation_type='Sync',
            x_fc_log_type='None'
        )
        request = fc20230330_models.InvokeFunctionRequest(
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