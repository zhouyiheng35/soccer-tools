from langchain_core.tools import StructuredTool
from typing import Type
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import json

from dotenv import load_dotenv
load_dotenv()

from alibabacloud_fc20230330.client import Client as FC20230330Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_darabonba_stream.client import Client as StreamClient
from alibabacloud_fc20230330 import models as fc20230330_models
from alibabacloud_tea_util import models as util_models

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

class DetectLeagueInput(BaseModel):
    team: str = Field(
        description="Team name, can be in Chinese or English"    
    )

class LoadTeamMatchesInput(BaseModel):
    league: str = Field(
        description="League code, e.g. E0 for Premier League"
    )
    team: str = Field(
        description="Team name"
    )

class QueryMatchesInput(BaseModel):
    matches: List[Dict[str, Any]] = Field(
        description="List of match records"
    )
    team: str = Field(
        description="Team name to query"
    )
    date: Optional[str] = Field(
        default=None,
        description="Date filter (YYYY-MM-DD)"
    )
    result: Optional[str] = Field(
        default=None,
        description="win / lose / draw"
    )
    home_or_away: Optional[str] = Field(
        default=None,
        description="home or away"
    )

class ChangeScoreInput(BaseModel):
    match: list[dict] = Field(
        description="List of match records"
    )
    home_score: int = Field(
        description="The goal number of home team"
    )
    away_score: int = Field(
        description="The goal number of away team"
    )

class AddMatchInput(BaseModel):
    league: str = Field(
        description="The league code(e.g., 'E0', 'D1', ...) which the team belongs to through 'detect_league' tool"
    )
    date: str = Field(
        description="The date of the new match"  
    )
    time: str = Field(
        description="The time of the new match"  
    )
    home: str = Field(
        description="The home team's name of the new match"
    )
    away: str = Field(
        description="The away team's name of the new match"
    )
    home_score: int = Field(
        default=0,
        description="The goal number of home team"
    )
    away_score: int = Field(
        default=0,
        description="The goal number of away team"
    )

class DeleteMatchesInput(BaseModel):
    matches: list[dict] = Field(
        description="List of match records"
    )


TOOL_INPUT_MODELS: dict[str, Type[BaseModel]] = {
    "detect_league": DetectLeagueInput,
    "load_team_matches": LoadTeamMatchesInput,
    "query_matches": QueryMatchesInput,
    "change_score": ChangeScoreInput,
    "add_match": AddMatchInput,
    "delete_matches": DeleteMatchesInput,
}


def Ali_tool_wrapper(tool_name: str) -> StructuredTool:
    """
    LangChain Tool wrapper
    - tool_name 来自 mytools
    - schema 来自你本地定义的 Pydantic
    - 执行走 FC
    """

    if tool_name not in TOOL_INPUT_MODELS:
        raise ValueError(f"No input schema defined for tool: {tool_name}")

    args_schema = TOOL_INPUT_MODELS[tool_name]

    # ⚠️ 注意：lambda 里用 _tool_name 绑定，避免闭包坑
    def _call_fc(**kwargs):
        return AliFC.call_fc_function(
            args={
                "tool": tool_name,
                "args": kwargs
            }
        )

    return StructuredTool.from_function(
        name=tool_name,
        description=f"Call tool `{tool_name}` via Aliyun FC",
        args_schema=args_schema,
        func=_call_fc,
    )