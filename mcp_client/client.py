import asyncio
import sys
import os
import anthropic
import json # Added for pretty printing tool results
from typing import Any, Dict, List, Optional, cast # Added for type hinting
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL")
# ANTHROPIC_API_KEY is read automatically from environment by the SDK
MAX_CONVERSATION_TURNS = 10 # Limit conversation length to prevent infinite loops
MAX_TOOL_ITERATIONS_PER_TURN = 10 # Limit consecutive tool calls for a single user request

# --- Anthropic LLM Interaction with Tool Use ---

async def call_anthropic_with_tools(
    client: anthropic.AsyncAnthropic,
    messages: List[Dict[str, Any]],
    tools: List[types.Tool],
    system_prompt: Optional[str] = None,
) -> anthropic.types.Message:
    """
    Calls the Anthropic API, passing available tools and handling system prompt.
    """
    print(f"\n--- Calling Anthropic (model: {ANTHROPIC_MODEL}) ---")
    print(f"Messages ({len(messages)}):")
    for msg in messages:
        print(f"  Role: {msg['role']}, Content: '{str(msg['content'])[:100]}...'")

    # Format tools for Anthropic API
    anthropic_tools = []
    for tool in tools:
        # Attempt to directly use an existing input_schema attribute from the MCP Tool type
        input_schema = getattr(tool, 'inputSchema', None)

        # Basic validation: Check if schema exists and is a dictionary
        if not isinstance(input_schema, dict):
            print(f"Warning: Skipping tool '{tool.name}'. Missing or invalid 'inputSchema' attribute (type: {type(input_schema)}).")
            continue

        # If input_schema is valid, use it directly
        anthropic_tools.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": input_schema, # Use the schema directly from the Tool object
        })

    print(f"Tools provided to LLM ({len(anthropic_tools)}):")
    for tool in anthropic_tools:
        print(f"  - {tool['name']}: {tool['description']}")

    request_params = {
        "model": ANTHROPIC_MODEL,
        "messages": messages,
        "tools": anthropic_tools,
        "max_tokens": 1024,
    }
    if system_prompt:
        request_params["system"] = system_prompt

    try:
        response = await client.messages.create(**request_params)
        print(f"--- Anthropic Response (Stop Reason: {response.stop_reason}) ---")
        # Print content blocks
        for block in response.content:
             if isinstance(block, anthropic.types.TextBlock):
                 print(f"  Content: '{block.text[:100]}...'")
             elif isinstance(block, anthropic.types.ToolUseBlock):
                 print(f"  Tool Use Request: {block.name}(id={block.id}, input={block.input})")
        return response
    except anthropic.APIError as e:
        print(f"!! Anthropic API Error: {e}")
        # Re-raise or handle more gracefully if needed
        raise


# --- MCP Client Logic (Interactive Agent) ---

async def run_interactive_client():
    """
    Runs an interactive client that takes user input, uses Anthropic for planning,
    and calls MCP server tools when requested by the LLM.
    """
    # --- Server Configuration ---
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

    print(f"Attempting to start MCP server using: {server_command} {' '.join(server_args)}")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable not set.")
        return # Exit if key is missing

    print("Starting Interactive MCP Client...")

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("stdio client connected to server process.")
            # NOTE: No sampling_callback needed for this interactive client
            async with ClientSession(read_stream, write_stream) as session:
                print("MCP ClientSession starting initialization...")
                init_result = await session.initialize()
                print("MCP ClientSession initialized.")
                print(f"Server capabilities: {init_result.capabilities}")

                # Discover available tools from the server
                available_tools: List[types.Tool] = []
                if init_result.capabilities and getattr(init_result.capabilities, 'tools', None):
                    try:
                        list_tools_result = await session.list_tools()
                        # Access the .tools attribute of the result object
                        if hasattr(list_tools_result, 'tools') and isinstance(list_tools_result.tools, list):
                            available_tools = list_tools_result.tools
                        else:
                            print("Warning: Could not extract tools list from list_tools() result.")
                            # Log the result type/structure for debugging if needed
                            # print(f"Debug: list_tools() returned type {type(list_tools_result)}")

                        print(f"\nDiscovered Tools ({len(available_tools)}):")
                        for tool in available_tools:
                            print(f"  - {tool.name}: {tool.description}")
                    except Exception as e:
                        print(f"Error listing tools: {e}")
                        # Optionally log traceback
                        # import traceback
                        # traceback.print_exc()
                else:
                    print("Warning: Server does not report tool capability. Tool use may not function.")

                # Initialize Anthropic client
                anthropic_client = anthropic.AsyncAnthropic()

                # Conversation history
                conversation_history: List[Dict[str, Any]] = []
                turn_count = 0

                print("\n--- Enter your request (or type 'quit' to exit) ---")

                # Outer loop for user turns
                while turn_count < MAX_CONVERSATION_TURNS:
                    user_input = await asyncio.to_thread(input, "> ")
                    if user_input.lower() == 'quit':
                        break

                    # Add user message to history
                    conversation_history.append({"role": "user", "content": user_input})

                    # Inner loop for handling LLM responses and tool calls for this turn
                    tool_iterations = 0
                    while tool_iterations < MAX_TOOL_ITERATIONS_PER_TURN:
                        # --- Call LLM --- 
                        # Use a temporary copy of history if planning fails, 
                        # but for now, we modify the main history directly.
                        llm_response = await call_anthropic_with_tools(
                            anthropic_client, conversation_history, available_tools
                        )

                        # --- Process LLM Response --- 
                        # Append assistant's response message(s) to history immediately
                        # This includes text and potential tool_use blocks
                        response_messages = []
                        assistant_response_content = [] # Collect blocks for the single assistant message
                        has_text_block = False
                        has_tool_use_block = False

                        for block in llm_response.content:
                            if isinstance(block, anthropic.types.TextBlock):
                                assistant_response_content.append(block.to_dict())
                                has_text_block = True
                            elif isinstance(block, anthropic.types.ToolUseBlock):
                                assistant_response_content.append(block.to_dict())
                                has_tool_use_block = True
                        
                        # Add the assistant message (potentially with tool use requests) to history
                        if assistant_response_content:
                            conversation_history.append({"role": "assistant", "content": assistant_response_content})
                        else:
                            # Handle cases where the response might be empty or unexpected
                            print("Warning: Assistant response content was empty.")
                            # Break the inner loop if there's nothing to process
                            break 

                        # --- Check for Tool Calls --- 
                        if llm_response.stop_reason == "tool_use" and has_tool_use_block:
                            tool_iterations += 1
                            print(f"--- Executing Tool Calls (Iteration {tool_iterations}/{MAX_TOOL_ITERATIONS_PER_TURN}) --- ")
                            tool_results = []
                            # Filter for the dictionaries representing tool use blocks - CORRECTED
                            tool_use_block_dicts = [block for block in assistant_response_content if block.get("type") == "tool_use"]

                            # Iterate through the dictionaries directly (already corrected)
                            for tool_block_dict in tool_use_block_dicts:
                                # Safely get required fields from the dictionary (already corrected)
                                tool_name = tool_block_dict.get("name")
                                tool_input = tool_block_dict.get("input")
                                tool_call_id = tool_block_dict.get("id")
                                print(f"  Attempting call: {tool_name}({tool_input}) [ID: {tool_call_id}]")

                                try:
                                    tool_output = await session.call_tool(name=tool_name, arguments=tool_input)
                                    print(f"  Tool {tool_name} Result: {json.dumps(tool_output, indent=2)}")
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_call_id,
                                        "content": str(tool_output), # Ensure content is string
                                    })
                                except Exception as e:
                                    print(f"  !! Error calling tool {tool_name}: {e}")
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_call_id,
                                        "content": f"Error executing tool: {e}",
                                        "is_error": True
                                    })

                            # Add tool results to conversation history for the next LLM call in the inner loop
                            conversation_history.append({
                                "role": "user", # Per Anthropic docs, tool results follow as a user message
                                "content": tool_results
                            })
                            # Continue the inner loop to call LLM again with tool results
                            continue 
                        
                        # --- No Tool Use or Tool Loop Finished --- 
                        else:
                            # If there was a text block in the last response, print it as the final answer
                            final_text = ""
                            for block_dict in assistant_response_content:
                                if block_dict.get("type") == "text":
                                    final_text += block_dict.get("text", "")
                            
                            if final_text:
                                print(f"\nAssistant:\n{final_text}")
                            elif llm_response.stop_reason != "tool_use":
                                print(f"\nAssistant finished without text output (Stop Reason: {llm_response.stop_reason}).")
                            else: # Hit tool iteration limit
                                print(f"\nAssistant finished due to reaching tool iteration limit ({MAX_TOOL_ITERATIONS_PER_TURN}). No final text output.")
                            
                            # Break the inner loop, ready for next user input
                            break 
                    
                    # End of inner loop (for single user request) 
                    turn_count += 1
                    if turn_count >= MAX_CONVERSATION_TURNS:
                        print("\nReached max conversation turns.")
                
                # End of outer loop (user turns)
                print("\nExiting interactive client.")

    except FileNotFoundError:
        print(f"Error: Server command not found: '{server_command}'")
    except anthropic.AuthenticationError:
        print("Error: Anthropic authentication failed. Ensure ANTHROPIC_API_KEY is set.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

    print("Interactive MCP Client finished.")


if __name__ == "__main__":
    print("Starting Interactive MCP Client application...")
    print("----------------------------------------------")
    asyncio.run(run_interactive_client()) 