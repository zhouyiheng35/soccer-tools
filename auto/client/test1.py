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

TOOL_NAME_MAP = {
    "detect_league": "tools.detect_league.detect_league",
    "load_team_matches": "tools.load_team_matches.load_team_matches",
    "query_matches": "tools.query_matches.query_matches",
    "change_score": "tools.change_score.change_score",
    "add_match": "tools.add_match.add_match",
    "delete_matches": "tools.delete_matches.delete_matches"
}

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

class Agent:
    def __init__(self):
        self.client = AliFC.create_client()
        self.tools = self.get_tools()
        self.agent = self.create()

    def get_tools(self):
        raw = AliFC.call_fc_function("tools.list_tools.list_tools", {})
        tools_data = raw.get("result", {}).get("tools", [])
        tool_objects = []

        for t in tools_data:
            short_name = t["name"]
            args_schema = self.get_schema_for_tool(short_name)
            description = t.get("description", "")
            # 参数描述
            params = t.get("parameters", {}).get("properties", {})
            param_desc = "\n".join(f"{k} ({v.get('type')}): {v.get('description','')}" for k,v in params.items())
            description += f"\nParameters:\n{param_desc}"

            # 工具函数封装
            def make_tool_func(tool_name):
                def tool_func(**kwargs):
                    full_name = TOOL_NAME_MAP[tool_name]
                    return AliFC.call_fc_function(full_name, kwargs)
                return tool_func

            tool_objects.append(
                StructuredTool.from_function(
                    name=short_name,
                    description=description,
                    func=make_tool_func(short_name),
                    args_schema=args_schema
                )
            )
        return tool_objects

    def get_schema_for_tool(self, name: str):
        return {
            "detect_league": DetectLeagueInput,
            "load_team_matches": LoadTeamMatchesInput,
            "query_matches": QueryMatchesInput,
            "change_score": ChangeScoreInput,
            "add_match": AddMatchInput,
            "delete_matches": DeleteMatchesInput
        }.get(name)


    def create(self):
        llm = ChatOpenAI(
            model=os.getenv("MODEL"),
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        agent = create_agent(
            llm,
            self.tools,
            system_prompt=(
                "You are an AI agent designed to solve tasks by using tools. "
                "You don't know any team information, don't guess by yourself. "
                "When a league is needed, you MUST call detect_league. "
                "Do not answer using your own knowledge if a tool can be used."
            )
        )
        return agent
    
    async def answer(self, query: str):
        async for chunk in self.agent.astream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="updates",
        ):
            for step, data in chunk.items():
                print(f"step: {step}")
                print(f"content: {data['messages'][-1].content_blocks}")

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

    @staticmethod
    def call_list_tools() -> List[dict]:
        raw = AliFC.call_fc_function("list_tools", {})
        return raw.get("tools", [])


if __name__ == '__main__':
    agent = Agent()
    # query = "帮我新增一场比赛，时间是2022年2月2日，主队是马赛，客队是巴黎圣日尔曼，比分是主队0，客队3"
    query = "请告诉我马赛的所有比赛情况"
    asyncio.run(agent.answer(query))