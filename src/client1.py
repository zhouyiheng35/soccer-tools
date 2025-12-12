import asyncio
import os
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from common.utils.Ch2En import TEAM_NAME_MAP

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

load_dotenv()


async def run_agent_until_done(agent, user_input, tools):
    # 步骤 1：初始化历史消息（正确）
    messages = [HumanMessage(content=user_input)]
    print("\n=== ReAct 循环开始 ===")

    while True:
        # 步骤 2：让模型根据历史消息推理下一步
        step = await agent.ainvoke({"messages": messages})
        new_messages = step["messages"]

        # 找到模型最新输出的消息（必须对比长度）
        llm_messages = new_messages[len(messages):]

        

        for msg in llm_messages:
            if isinstance(msg, AIMessage):
                print(f"[LLM] {msg.content}")

            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                # 多工具也能支持
                for call in tool_calls:
                    name = call["name"]
                    args = call.get("args") or call.get("arguments")
                    tool_call_id = call["id"]

                    if "team" in args:
                        chinese_name = args["team"]
                        if chinese_name in TEAM_NAME_MAP:
                            english_name = TEAM_NAME_MAP[chinese_name]
                            args["team"] = english_name

                    print(f"[Tool Call] name={name}, args={args}")

                    # 找到工具对象
                    tool = next(t for t in tools if t.name == name)

                    # 执行工具
                    result = await tool.ainvoke(args)
                    print(f"[Tool Output] {result}")

                    if isinstance(result, (dict, list)):
                        content = result  # LangChain 会自动处理 dict，不能 JSON 序列化
                    else:
                        content = str(result)

                    # ****** 核心修复点：Append 到历史消息 messages，而不是 new_messages ******
                    messages.append(
                        ToolMessage(
                            tool_call_id=tool_call_id,
                            name=name,
                            content=content
                        )
                    )

        # 步骤 3：把 LLM 的新消息加入历史（正确）
        messages.extend(llm_messages)

        # 步骤 4：退出条件
        if not getattr(messages[-1], "tool_calls", None):
            print("\n=== ReAct 循环结束（模型完成任务） ===")
            return messages[-1].content

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

    # question = "请告诉我霍芬海姆所有在2023年10月28日的比赛情况"
    question = "请帮我把霍芬海姆在2023年8月19日的比赛比分进行更改，主队0球，客队8球"

    final_answer = await run_agent_until_done(agent, question, tools)

    print("\n=== 最终输出 ===")
    print(final_answer)


if __name__ == "__main__":
    asyncio.run(main())