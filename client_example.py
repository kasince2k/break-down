import asyncio
import sys
import os

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# --- Placeholder for LLM Call ---

async def placeholder_llm_call(messages: list[types.PromptMessage]) -> types.CreateMessageResult:
    """
    Placeholder function for making a call to an LLM.
    Replace this with your actual LLM interaction logic if needed for this example.
    """
    print(f"[Example Client] Placeholder LLM received {len(messages)} messages. Last message:")
    if messages:
        last_message = messages[-1]
        if isinstance(last_message.content, types.TextContent):
            print(f"  Role: {last_message.role}, Content: '{last_message.content.text[:100]}...'")
        else:
             print(f"  Role: {last_message.role}, Content Type: {type(last_message.content)}")

    # Simulate a simple LLM response
    response_text = "This is a placeholder response from the example client's LLM."

    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(type="text", text=response_text),
        model="placeholder-model",
        stopReason="endTurn",
    )


# --- MCP Client Logic ---

async def handle_sampling_message(
    params: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    """
    Callback function to handle sampling requests from the MCP server.
    This function will call the placeholder LLM function.
    """
    print(f"[Example Client] Received sampling request with {len(params.messages)} messages.")
    return await placeholder_llm_call(params.messages)


async def run_example_client():
    """
    Sets up and runs the example passive MCP client.
    Connects to the server and waits for sampling requests.
    """
    # --- Server Configuration (Copied from main client) ---
    server_command = 'node'
    server_args = [
        '/Users/ashwin/side_projects/obsidian-mcp/build/main.js',
        '/Users/ashwin/personal/Obsidian/Sample/Extra/Extra/Extra/Test/Test Vault'
    ]
    server_env = None

    server_params = StdioServerParameters(
        command=server_command,
        args=server_args,
        env=server_env,
    )

    print(f"[Example Client] Attempting to start MCP server using: {server_command} {' '.join(server_args)}")
    print("[Example Client] Starting passive MCP client and connecting to server process...")
    try:
        # Connect to the server process via stdio
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("[Example Client] stdio client connected to server process.")

            # Start an MCP client session, providing the sampling callback
            async with ClientSession(
                read_stream, write_stream, sampling_callback=handle_sampling_message
            ) as session:
                print("[Example Client] MCP ClientSession starting...")
                initialization_result = await session.initialize()
                print("[Example Client] MCP ClientSession initialized.")
                server_capabilities = initialization_result.capabilities
                print(f"[Example Client] Server capabilities: {server_capabilities}")

                # Check if the server supports sampling (required for the callback)
                if not server_capabilities or not getattr(server_capabilities, 'sampling', False):
                     print("[Example Client] Warning: Connected server does not explicitly report sampling capability.")
                     print("[Example Client] The handle_sampling_message callback might not be invoked.")


                print("\n[Example Client] Client is running and connected to the server.")
                print("[Example Client] Waiting for sampling requests from the server...")
                # Keep the client running to handle callbacks indefinitely
                await asyncio.Future() # Wait forever

    except FileNotFoundError:
        print(f"[Example Client] Error: Server command not found: '{server_command}'")
    except Exception as e:
        print(f"\n[Example Client] Error during client execution: {e}")

    print("[Example Client] MCP Client finished.")


if __name__ == "__main__":
    print("[Example Client] Starting Example MCP Client application...")
    print("------------------------------------------------------")
    asyncio.run(run_example_client()) 