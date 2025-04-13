import asyncio

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)


async def get_tools_async():
    """Gets tools from the File System MCP Server."""
    print("Attempting to connect to MCP Filesystem server...")
    tools, exit_stack = await MCPToolset.from_server(
        # Use StdioServerParameters for local process communication
        connection_params=StdioServerParameters(
            command="npx",  # Command to run the server
            args=[
                "-y",  # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                "/Users/roshanmurthy/Desktop/testvault/test1/test1",
            ],
        )
    )
    print("MCP Toolset created successfully.")
    # MCP requires maintaining a connection to the local MCP Server.
    # exit_stack manages the cleanup of this connection.
    return tools, exit_stack


if __name__ == "__main__":
    try:
        asyncio.run(get_tools_async())
    except Exception as e:
        print(f"An error occurred: {e}")

ag = Agent()
