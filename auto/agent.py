import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from Ali_tool_wrapper import Ali_tool_wrapper
from FC_client import AliFC

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