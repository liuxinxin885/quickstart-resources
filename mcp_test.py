import asyncio
import sys
import os
import pathlib
ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(str(ROOT_DIR))
from dotenv import load_dotenv
from aggent.openai import AsyncOpenAI
from aggent.agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from aggent.agents.mcp import MCPServerStdio, MCPServerSse
from aggent.agents import Agent, gen_trace_id, trace, Runner, Tool, function_tool, set_tracing_disabled, trace, set_default_openai_client
from contextlib import asynccontextmanager, AsyncExitStack, suppress

load_dotenv()

client_qwen = AsyncOpenAI(base_url=os.getenv("QWEN_BASE_URL"),
                         api_key=os.getenv("QWEN_API_KEY"))

set_default_openai_client(client_qwen)
set_tracing_disabled(disabled=True)

model = 'qwen3-235b-a22b'

async def cleanup_servers(servers):
    """确保所有服务器正确关闭"""
    for server in servers:
        with suppress(Exception):
            if hasattr(server, 'disconnect'):
                await server.disconnect()
        with suppress(Exception):
            if hasattr(server, 'close'):
                await server.close()
        with suppress(Exception):
            if hasattr(server, '_transport') and server._transport is not None:
                server._transport.close()

async def main():
    # 定义两个服务的参数
    service_filesystem_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem",
                # '/home/liuxx/Desktop/python/csh/hi-dolphin-openai-agent/hi-dolphin-agent-extension-main/output'
                '/Users/lxx/Documents/代码/quickstart-resources/aggent/output'],
        "name": "filesystem service",
    }
    
    service_fetchweb_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {
            "PUPPETEER_LAUNCH_OPTIONS": r'{"executablePath": "/usr/bin/google-chrome", "headless": true}',
            "ALLOW_DANGEROUS": "true"
        },
        "name": "fetch web service",
    }

    service_pgdatabase_params = {
        "mcpServers": {
            "polardb-postgresql-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                # "/home/liuxx/Desktop/python/csh/alibabacloud-polardb-mcp-server-master/polardb-postgresql-mcp-server",
                "/Users/lxx/Documents/代码/quickstart-resources/polardb-postgresql-mcp-server",
                "run",
                "server.py"
            ],
            "env": {
                "POLARDB_POSTGRESQL_HOST": "polar-prd-rw.csntcorp.com",
                "POLARDB_POSTGRESQ_PORT": "1921",
                "POLARDB_POSTGRESQ_USER": "chenshuhang",
                "POLARDB_POSTGRESQL_PASSWORD": "WVca+e8TUF2!D3",
                "POLARDB_POSTGRESQL_DBNAME": "sdc-prd",
                "RUN_MODE": "stdio",
                "POLARDB_POSTGRESQL_ENABLE_UPDATE": "false",
                "POLARDB_POSTGRESQL_ENABLE_UPDATE": "false",
                "POLARDB_POSTGRESQL_ENABLE_INSER": "false",
                "POLARDB_POSTGRESQL_ENABLE_DDL": "false"
            },
            "name": "postgresql database connection"
            }
        }
    }

    # 使用AsyncExitStack管理多个服务的生命周期
    try:
        async with AsyncExitStack() as stack:
            try:
                # 启动第一个服务
                server_filesystem = await stack.enter_async_context(
                    MCPServerStdio(
                        name=service_filesystem_params["name"],
                        params={
                            "command": service_filesystem_params["command"],
                            "args": service_filesystem_params["args"],
                        },
                    )
                )
                
                # 启动第二个服务
                server_pgdatabase = await stack.enter_async_context(
                    MCPServerStdio(
                        name=service_pgdatabase_params["mcpServers"]["polardb-postgresql-mcp-server"]["name"],
                        params={
                            "command": service_pgdatabase_params["mcpServers"]["polardb-postgresql-mcp-server"]["command"],
                            "args": service_pgdatabase_params["mcpServers"]["polardb-postgresql-mcp-server"]["args"],
                        },
                    )
                )

                servers = [server_filesystem, server_pgdatabase]

                # 显式连接服务
                await asyncio.wait_for(
                    asyncio.gather(*[s.connect() for s in servers]),
                    timeout=30.0
                )

                # 创建Agent
                trace_id = gen_trace_id()
                agent = Agent(
                    name="Assistant",
                    model=OpenAIChatCompletionsModel(model=model, openai_client=client_qwen),
                    instructions="请根据用户输入的SQL代码进行数据库的调用，并将数据库返回的结果保存成xlsx文件到output文件夹下",
                    mcp_servers=[server_filesystem, server_pgdatabase],
                )
                
                with trace(workflow_name="MCP Multi-Service Example", trace_id=trace_id):
                    print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
                    message = "请根据用户输入的SQL代码进行数据库的调用:select * from sdc_dw.fm_vessel limit 1，并将数据库返回的结果保存成0611.xlsx文件到output文件夹下，并总结数据库返回的结果"

                    # 运行Agent
                    result = await Runner.run(starting_agent=agent, input=message)
                    return result

            except Exception as e:
                print(f"An error occurred: {e}")
                raise
            finally:
                pass

    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        # 确保所有服务正确关闭
        await cleanup_servers(servers)
        # 清理任何挂起的任务
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            with suppress(asyncio.CancelledError, RuntimeError):
                await task
        # 给事件循环一个清理的机会
        await asyncio.sleep(0.1)

def run_main():
    # 设置事件循环策略
    print(sys.platform)

    # if sys.platform == 'win32':
    #     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(main())
        print(result)
    except KeyboardInterrupt:
        print("Process interrupted by user")
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        # 额外清理步骤
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            loop.close()
            # 重置事件循环，防止后续操作使用已关闭的循环
            asyncio.set_event_loop(None)

if __name__ == "__main__":
    # result = asyncio.run(main())
    # print(result)
    run_main()
    import gc 
    gc.collect()
    