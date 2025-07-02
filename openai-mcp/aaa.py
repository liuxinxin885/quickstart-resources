import asyncio
import os
import shutil
import pathlib
import sys
# ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.resolve()
ROOT_DIR='/Users/lxx/Documents/代码/quickstart-resources'
print(ROOT_DIR)
sys.path.append(str(ROOT_DIR))
# from aggent.agents import Agent, Runner, gen_trace_id, trace,set_default_openai_client,set_tracing_disabled,OpenAIChatCompletionsModel
# from aggent.agents.mcp import MCPServer, MCPServerStdio
# from aggent.openai import AsyncOpenAI
from agents import Agent, Runner, gen_trace_id, trace,set_default_openai_client,set_tracing_disabled,OpenAIChatCompletionsModel
from agents.mcp import MCPServer, MCPServerStdio
from openai import AsyncOpenAI
from dotenv import load_dotenv

API_KEY = "sk-0079be2ceda64ece81e0810e2b6c7be9"  # 替换为你的 OpenAI API Key
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # OpenAI API 基础地址
MODEL = "qwen-turbo"  # 使用的模型（如 gpt-3.5-turbo, gpt-4）
load_dotenv()

client_qwen = AsyncOpenAI(base_url=API_BASE,
                         api_key=API_KEY)

set_default_openai_client(client_qwen)
set_tracing_disabled(disabled=True)

model =MODEL

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        model=OpenAIChatCompletionsModel(model=model, openai_client=client_qwen),
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        mcp_servers=[mcp_server],
    )

    # List the files it can read
    message = "Read the files and list them."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Ask about books
    message = "What is my #1 favorite book?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Ask a question that reads then reasons.
    message = "Look at my favorite songs. Suggest one new song that I might like."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")
    samples_dir = '/Users/lxx/Documents/代码/quickstart-resources/sample_files'
    print(f"Using samples directory: {samples_dir}")
    # samples_dir=''
    a={
        "mcpServers": {
            "mcp-server-chart": {
            "command": "npx",
            "args": [
                "-y",
                "@antv/mcp-server-chart"
            ]
            }
        }
        }
    async with MCPServerStdio(
        name="Filesystem Server, via npx",

        
        # params=a['mcpServers']['mcp-server-chart'],
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Filesystem Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)

# npx -y @modelcontextprotocol/server-filesystem /Users/lxx/Documents/代码/quickstart-resources/sample_files
if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())