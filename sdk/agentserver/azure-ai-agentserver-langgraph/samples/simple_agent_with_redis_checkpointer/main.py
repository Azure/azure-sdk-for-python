import asyncio
import os

from importlib.metadata import version
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from redis.asyncio import Redis

from azure.ai.agentserver.langgraph import from_langgraph

load_dotenv()

client = Redis(
    host=os.getenv("CHECKPOINTER_REDIS_URL"),
    port=os.getenv("CHECKPOINTER_REDIS_PORT"),
    password=os.getenv("CHECKPOINTER_REDIS_KEY"),
    ssl=True,
    decode_responses=False,  # RedisSaver expects bytes
)

deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
model = AzureChatOpenAI(model=deployment_name)


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


@tool
def calculator(expression: str) -> str:
    """Evaluates mathematical expression"""
    try:
        maths_result = eval(expression)
        return str(maths_result)
    except Exception as e:
        return f"Error: {str(e)}"


tools = [get_word_length, calculator]


def create_agent(model, tools, checkpointer):
    # for different langgraph versions
    langgraph_version = version("langgraph")
    if langgraph_version < "1.0.0":
        from langgraph.prebuilt import create_react_agent

        return create_react_agent(model, tools, checkpointer=checkpointer)
    else:
        from langchain.agents import create_agent

        return create_agent(model, tools, checkpointer=checkpointer)


async def run_async():
    # Pass the configured client to RedisSaver
    # adapter uses astream/ainvoke so we need async checkpointer
    saver = AsyncRedisSaver(redis_client=client)
    await saver.asetup()

    executor = create_agent(model, tools, checkpointer=saver)
    # start server with async
    await from_langgraph(executor).run_async()


if __name__ == "__main__":
    # host the langgraph agent
    asyncio.run(run_async())
