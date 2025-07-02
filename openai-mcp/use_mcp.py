# highlight-next-line
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from openai import AsyncOpenAI

# highlight-next-line
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Replace with absolute path to your math_server.py file
            "args": ["/Users/lxx/Documents/代码/openai-mcp/mcp_stdio.py"],
            "transport": "stdio",
        },
        "weather": {
            # Ensure you start your weather server on port 8000
            "url": "/Users/lxx/Documents/代码/openai-mcp/mcp_streamable.py",
            "transport": "streamable_http",
        }
    }
)
# highlight-next-line
from agents import Agent, Runner, gen_trace_id, trace,set_default_openai_client,set_tracing_disabled,OpenAIChatCompletionsModel

API_KEY = "sk-0079be2ceda64ece81e0810e2b6c7be9"  # 替换为你的 OpenAI API Key
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # OpenAI API 基础地址
MODEL = "qwen-turbo"  # 使用的模型（如 gpt-3.5-turbo, gpt-4）
client_qwen = AsyncOpenAI(base_url=API_BASE,
                         api_key=API_KEY)

set_default_openai_client(client_qwen)
set_tracing_disabled(disabled=True)
async def main():
    tools = await client.get_tools()
    agent = create_react_agent(
        "anthropic:claude-3-7-sonnet-latest",
        # highlight-next-line
        tools
    )
    agent = Agent(
        name="Assistant",
        model=OpenAIChatCompletionsModel(model=MODEL, openai_client=client_qwen),
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        mcp_servers=[mcp_server],
    )
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(tools)

if __name__ == "__main__":
    asyncio.run(main())  # 运行 async 函数
