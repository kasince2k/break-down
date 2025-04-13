import asyncio
import sys

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# --- Placeholder for LLM Call ---

async def placeholder_llm_call(messages: list[types.PromptMessage]) -> types.CreateMessageResult:
    """
    Placeholder function for making a call to an LLM.
    Replace this with your actual LLM interaction logic.
    """
    print(f"Placeholder LLM received {len(messages)} messages. Last message:")
    if messages:
        last_message = messages[-1]
        if isinstance(last_message.content, types.TextContent):
            print(f"  Role: {last_message.role}, Content: '{last_message.content.text[:100]}...'")
        else:
             print(f"  Role: {last_message.role}, Content Type: {type(last_message.content)}")

    # Simulate a simple LLM response
    response_text = "This is a placeholder response from the LLM."

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
    print(f"Received sampling request with {len(params.messages)} messages.")
    return await placeholder_llm_call(params.messages)


async def run_client():
    """
    Sets up and runs the MCP client.
    """
    # --- Server Configuration ---
    # Updated to connect to the Obsidian MCP server
    server_command = 'node'
    server_args = [
        '/Users/ashwin/side_projects/obsidian-mcp/build/main.js',
        '/Users/ashwin/personal/Obsidian/Sample/Extra/Extra/Extra/Test/Test Vault'
    ]
    server_env = None # Optional: Dictionary of environment variables if needed

    server_params = StdioServerParameters(
        command=server_command,
        args=server_args,
        env=server_env,
    )

    print(f"Attempting to start MCP server using: {server_command} {' '.join(server_args)}")
    print("Starting MCP client and connecting to server process...")
    try:
        # Connect to the server process via stdio
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("stdio client connected to server process.")

            # Start an MCP client session, providing the sampling callback
            async with ClientSession(
                read_stream, write_stream, sampling_callback=handle_sampling_message
            ) as session:
                print("MCP ClientSession starting...")
                initialization_result = await session.initialize()
                print("MCP ClientSession initialized.")
                server_capabilities = initialization_result.capabilities
                print(f"Server capabilities: {server_capabilities}")

                # Check if the server supports sampling (required for the callback)
                if not server_capabilities or not getattr(server_capabilities, 'sampling', False):
                     print("Warning: Connected server does not explicitly report sampling capability.")
                     print("The handle_sampling_message callback might not be invoked.")


                print("Client is running and connected to the server.")
                print("Waiting for sampling requests from the server...")
                # Keep the client running to handle callbacks indefinitely
                await asyncio.Future() # Wait forever

    except FileNotFoundError:
        print(f"Error: Server command not found: '{server_command}'")
        print("Please update the 'server_command' variable in client.py")
    except Exception as e:
        print(f"Error during client execution: {e}")
        print("Ensure the server command and arguments are correct and the server runs without errors.")

    print("MCP Client finished.")


if __name__ == "__main__":
    print("Starting MCP Client application...")
    print("-----------------------------------------")
    asyncio.run(run_client()) 