import os
import sys
import asyncio
from pathlib import Path
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console

class ObsidianChat:
    def __init__(self, vault_path: str, mcp_path: str):
        self.vault_path = vault_path
        self.mcp_path = mcp_path
        self.agent = None
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

    async def setup(self):
        """Set up the MCP server and create the agent"""
        try:
            # Setup server params for Obsidian MCP
            obsidian_mcp_server = StdioServerParams(
                command="node",
                args=[self.mcp_path, self.vault_path]
            )
            
            print("Initializing MCP server and tools...")
            # Get the tools from the MCP server
            tools = await mcp_server_tools(obsidian_mcp_server)
            print("MCP tools initialized successfully!")
            
            # Create the model client
            model_client = OpenAIChatCompletionClient(model="gemini-1.5-flash")
            
            # Create the agent with access to the MCP tools
            self.agent = AssistantAgent(
                name="obsidian_assistant",  # Fixed: removed space from name
                model_client=model_client,
                tools=tools,
                system_message="""You are an AI assistant that helps users interact with their Obsidian vault.
You have access to various tools to manage notes, files, and content in the vault.
When a user asks you to do something:
1. Analyze their request carefully
2. Explain what you plan to do
3. Use the appropriate tools to accomplish the task
4. Report back the results

Available tools:
- create-note: Create a new note in the vault
- list-available-vaults: List all available vaults
- edit-note: Edit an existing note
- search-vault: Search for content in the vault
- move-note: Move a note to a different location
- create-directory: Create a new directory
- delete-note: Delete a note (use with caution)
- add-tags: Add tags to a note
- remove-tags: Remove tags from a note
- rename-tag: Rename a tag across the vault
- read-note: Read the contents of a note
- read-canvas: Read a canvas file
- create-canvas: Create a new canvas
- edit-canvas: Edit an existing canvas
- delete-canvas: Delete a canvas

Always be careful with destructive operations (delete, move, etc).
Ask for confirmation before performing such operations.""",
                reflect_on_tool_use=True,  # Enable reflection on tool usage
                model_client_stream=True,  # Enable streaming for better UX
            )
            print("Agent initialized successfully!")
            
        except Exception as e:
            print(f"\nError during setup: {str(e)}")
            raise

    def print_welcome(self):
        """Print welcome message and available commands"""
        print("\n=== Obsidian Chat Assistant ===")
        print("Connected to vault:", self.vault_path)
        print("\nAvailable commands:")
        print("  /help     - Show this help message")
        print("  /quit     - Exit the chat")
        print("  /status   - Check connection status")
        print("\nStart chatting! Ask me anything about your Obsidian vault.")
        print("Examples:")
        print("  - Create a new note called 'Meeting Notes'")
        print("  - Search for notes containing 'python'")
        print("  - List all available vaults")
        print("=" * 30 + "\n")

    async def check_status(self):
        """Check the status of the agent and MCP server"""
        if self.agent is None:
            print("\nStatus: Not connected")
            print("Try restarting the chat to reconnect.")
        else:
            print("\nStatus: Connected")
            print(f"Vault path: {self.vault_path}")
            print("MCP server: Running")
            print("Agent: Ready")

    async def chat_loop(self):
        """Main chat loop"""
        self.print_welcome()
        
        try:
            # Initialize the agent and MCP server
            await self.setup()
            
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Handle commands
                if user_input.startswith("/"):
                    if user_input.lower() == "/quit":
                        break
                    elif user_input.lower() == "/help":
                        self.print_welcome()
                    elif user_input.lower() == "/status":
                        await self.check_status()
                    continue
                
                if not self.agent:
                    print("\nError: Not connected to the MCP server. Please restart the chat.")
                    continue
                
                # Run the agent with user input and stream the output
                try:
                    await Console(
                        self.agent.run_stream(
                            task=user_input,
                            cancellation_token=CancellationToken()
                        )
                    )
                except Exception as e:
                    print(f"\nError processing request: {str(e)}")

        except KeyboardInterrupt:
            print("\nExiting chat...")
        except Exception as e:
            print(f"\nError: {str(e)}")
        finally:
            print("\nGoodbye!")

async def main():
    # Use the paths from your environment
    vault_path = "/Users/keshavag/projects/break-down-vault"  # Update this
    mcp_path = "/Users/keshavag/projects/obsidian-mcp/build/main.js"  # Update this
    
    chat = ObsidianChat(vault_path, mcp_path)
    await chat.chat_loop()

if __name__ == "__main__":
    asyncio.run(main()) 