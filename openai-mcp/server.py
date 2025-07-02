# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("时间机器")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Start the MCP server
    # 客户端在本机运行
    # mcp.run(transport='stdio')
    # 在远程服务器上运行时，可以使用以下命令行启动MCP服务器
    # mcp.run(transport='sse')
    mcp.run(transport='streamable-http')
    # mcp.run(transport='steamable')