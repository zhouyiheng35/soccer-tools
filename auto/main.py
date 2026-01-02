import os
import json
from dotenv import load_dotenv
import asyncio

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from Ali_tool_wrapper import AliFC, Ali_tool_wrapper

load_dotenv()

mytools = [
    "detect_league",
    "load_team_matches",
    "query_matches",
    "add_match",
    "change_score",
    "delete_matches",
]

class Agent:
    def __init__(self):
        self.client = AliFC.create_client()
        self.tools = [Ali_tool_wrapper(tool) for tool in mytools]
        self.agent = self.create()

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

        
if __name__ == '__main__':
    agent = Agent()
    query = "请告诉我曼城的所有平局比赛情况"
    # query = "帮我新增一场比赛，时间是2026年1月1日20：00，主队是曼城，客队是曼联"
    # query = "帮我把利物浦的所有主场比赛删除"
    # query = "帮我把曼城2026年1月1日的比赛比分改成主队3，客队10"
    asyncio.run(agent.answer(query))