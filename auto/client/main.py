import asyncio
from agent.soccer_agent import SoccerAgent
from config.settings import check_required

if __name__ == "__main__":
    check_required()

    agent = SoccerAgent()
    asyncio.run(
        agent.answer("请问曼城属于哪个联赛")
    )