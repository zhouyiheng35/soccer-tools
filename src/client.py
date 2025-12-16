import os
import asyncio
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

async def main():
    client = MultiServerMCPClient(
        {
            "soccer": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    tools = await client.get_tools()

    llm = ChatOpenAI(
        model=os.getenv("MODEL"),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = create_agent(
        llm,
        tools,
        system_prompt=(
            "You are an AI agent designed to solve tasks by using tools. "
            "You don't know any team information, don't guess by yourself. "
            "When a league is needed, you MUST call detect_league. "
            "Do not answer using your own knowledge if a tool can be used."
        )
    )

    async for chunk in agent.astream(  
        {"messages": [{"role": "user", "content": "请告诉我科隆的所有比赛情况?"}]},
        stream_mode="updates",
    ):
        for step, data in chunk.items():
            print(f"step: {step}")
            print(f"content: {data['messages'][-1].content_blocks}")

if __name__ == "__main__":
    asyncio.run(main())