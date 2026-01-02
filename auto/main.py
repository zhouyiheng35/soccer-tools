import asyncio

from agent import Agent
        
agent = Agent()
query = "请告诉我萨索洛的全部比赛情况"
asyncio.run(agent.answer(query))