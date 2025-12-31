from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tools.registry import build_tools

from config.settings import (
    MODEL,
    BASE_URL,
    OPENAI_API_KEY,
)

class SoccerAgent:
    def __init__(self):
        self.tools = build_tools()
        self.llm = ChatOpenAI(
            model=MODEL,
            base_url=BASE_URL,
            api_key=OPENAI_API_KEY,
        )

        self.agent = create_agent(
            self.llm,
            self.tools,
            system_prompt=(
                "You are an AI agent designed to solve tasks by using tools. "
                "You don't know any team information, don't guess by yourself. "
                "When a league is needed, you MUST call detect_league. "
                "Do not answer using your own knowledge if a tool can be used."
            )
        )

    async def answer(self, query: str):
        async for chunk in self.agent.astream(
            {"messages": [{"role": "user", "content": query}]},
            stream_mode="updates",
        ):
            for step, data in chunk.items():
                print(f"step: {step}")
                print(f"content: {data['messages'][-1].content_blocks}")
