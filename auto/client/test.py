import os
import json
import asyncio

from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from alibabacloud_fc20230330.client import Client as FC20230330Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_darabonba_stream.client import Client as StreamClient
from alibabacloud_fc20230330 import models as fc20230330_models
from alibabacloud_tea_util import models as util_models

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

load_dotenv()

class Agent:
    def __init__(self):
        self.client = AliFC.create_client()
        self.tools = self.get_tools()

    def get_tools(self):
        raw = AliFC.call_fc_function("tools.list_tools.list_tools", {})
        tools_data = raw.get("result", {}).get("tools", [])
        return tools_data

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
    
    @staticmethod
    def call_fc_function(function_name: str, args: dict) -> dict:
        client = AliFC._client or AliFC.create_client()
        payload = {
            "tool": function_name,
            "args": args
        }
        body_stream = StreamClient.read_from_string(
            json.dumps(payload, ensure_ascii=False)
        )
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
        
if __name__ == '__main__':
    agent = Agent()
    print(agent.tools)