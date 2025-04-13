import os
import sys
import asyncio
import logging # Added for logging
from pathlib import Path
from dotenv import load_dotenv
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent # Removed UserProxyAgent
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ObsidianChat:
    def __init__(self, vault_path: str, mcp_path: str):
        self.vault_path = vault_path
        self.mcp_path = mcp_path
        self.executor: AssistantAgent | None = None
        self.planner: AssistantAgent | None = None
        # Removed: self.user_proxy
        
        # Check API keys and mandatory env vars
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        if not os.getenv("ANTHROPIC_MODEL"):
            raise ValueError("ANTHROPIC_MODEL environment variable not set")

    async def setup(self, tools: list):
        """Set up the planner and executor agents, receiving tools as input"""
        try:
            # --- Common Setup ---
            model_name = os.getenv("ANTHROPIC_MODEL") 
            logging.info(f"Using model: {model_name}")
            model_client = AnthropicChatCompletionClient(model=model_name)

            # --- Planner Setup ---
            self.planner = AssistantAgent(
                name="planner",
                model_client=model_client,
                system_message="""You are a task planner assistant.
Given a user request related to Obsidian, break it down into a clear, numbered, step-by-step plan.
Each step should correspond to a single action or tool use.
Do not execute any tools. Just describe the steps required.
Be concise. Output ONLY the numbered list of steps, each on a new line. Start with 1.

Example:
User: Create a note called 'Project Plan', tag it with #todo, and read it
Plan:
1. Create a note called 'Project Plan'
2. Add the tag 'todo' to the note 'Project Plan'
3. Read the note 'Project Plan'""",
                tools=[], # Explicitly no tools
            )
            logging.info("Planner agent initialized successfully!")

            # --- Executor Setup ---
            self.executor = AssistantAgent(
                name="obsidian_executor",
                model_client=model_client,
                tools=tools, # Use provided tools
                system_message="""You are an Obsidian Executor AI assistant.
You execute single-step tasks given to you, using the available tools.
Focus solely on executing the *current* step accurately.""",
                reflect_on_tool_use=False,
                model_client_stream=True, 
            )
            logging.info("Executor agent initialized successfully!")
            
        except Exception as e:
            logging.error(f"Error during agent setup: {str(e)}")
            raise

    def print_welcome(self):
        """Print welcome message and available commands"""
        print("\n=== Obsidian Chat Assistant (Plan & Execute) ===")
        print("Connected to vault:", self.vault_path)
        print("\nAvailable commands:")
        print("  /help     - Show this help message")
        print("  /quit     - Exit the chat")
        print("  /status   - Check connection status")
        print("\nStart chatting! Ask me anything about your Obsidian vault.")
        print("=" * 30 + "\n")

    async def check_status(self):
        """Check the status of the agents and MCP server"""
        # Basic check if agents are initialized
        if self.executor is None or self.planner is None:
            print("\nStatus: Agents not fully initialized")
        else:
            print("\nStatus: Agents Initialized")
            print(f"Vault path: {self.vault_path}")
            # Note: MCP server status is implicit if tools were loaded
            print("Planner Agent: Ready")
            print("Executor Agent: Ready")

    async def chat_loop(self):
        """Main chat loop using simplified Plan-and-Execute"""
        self.print_welcome()
        
        try:
            # --- Load MCP Tools --- 
            # Moved tool loading here, before agent setup
            logging.info("Initializing MCP server and tools...")
            obsidian_mcp_server = StdioServerParams(
                command="node",
                args=[self.mcp_path, self.vault_path]
            )
            tools = await mcp_server_tools(obsidian_mcp_server)
            logging.info("MCP tools initialized successfully!")

            # --- Setup Agents --- 
            await self.setup(tools) # Pass tools to setup
            
            while True:
                user_input = input("\nYou: ").strip()
                
                if user_input.startswith("/"):
                    if user_input.lower() == "/quit":
                        break
                    elif user_input.lower() == "/help":
                        self.print_welcome()
                    elif user_input.lower() == "/status":
                        await self.check_status()
                    continue
                
                if not self.planner or not self.executor:
                    logging.error("Error: Agents not initialized. Cannot proceed.")
                    break

                # --- Plan Step ---
                logging.info("[Planner] Generating plan...")
                plan_text = None
                try:
                    # Use run() method to get the plan TaskResult
                    plan_result = await self.planner.run(task=user_input)
                    
                    # Extract content from the TaskResult structure
                    if not hasattr(plan_result, 'messages') or not plan_result.messages:
                        logging.error(f"TaskResult missing messages: {plan_result}")
                        raise ValueError("Planner run did not return messages in TaskResult.")
                        
                    last_message = plan_result.messages[-1]
                    if not hasattr(last_message, 'content') or not last_message.content:
                        logging.error(f"Last message missing content: {last_message}")
                        raise ValueError("Planner message content is missing or empty.")

                    plan_text = last_message.content.strip()
                    if not plan_text:
                        raise ValueError("Planner returned an empty plan string.")

                    print(f"\nPlan:\n{plan_text}")
                except Exception as e:
                    logging.error(f"Error generating plan: {e}")
                    continue # Ask for new input

                # --- Execute Step ---
                plan_steps = [s.strip() for s in plan_text.split('\n') if s.strip() and s.strip()[0].isdigit()]
                
                if not plan_steps:
                     logging.warning("No valid steps found in the plan. Please try rephrasing.")
                     continue

                logging.info("Executing plan...")
                for i, step in enumerate(plan_steps):
                    step_text = step.split('.', 1)[-1].strip() # Remove numbering like "1. "
                    logging.info(f"[Executor] Executing: {step_text}")
                    try:
                        # Use Console wrapper for streaming UI
                        await Console(
                            self.executor.run_stream(
                                task=step_text, # Pass the step text without number
                                cancellation_token=CancellationToken()
                            )
                        )
                    except Exception as e:
                        logging.error(f"Error executing step '{step_text}': {e}")
                        logging.info("Stopping plan execution due to error.")
                        break # Stop executing further steps
                else:
                    logging.info("Plan execution finished.")

        except KeyboardInterrupt:
            print("\nExiting chat...")
        except Exception as e:
            logging.error(f"Fatal Error: {e}")
        finally:
            print("\nGoodbye!")

async def main():
    load_dotenv()
    
    # Get config from environment variables
    vault_path = os.getenv("VAULT_PATH")
    mcp_path = os.getenv("MCP_PATH")

    # Check if paths are set
    if not vault_path:
        raise ValueError("VAULT_PATH environment variable not set")
    if not mcp_path:
        raise ValueError("MCP_PATH environment variable not set")

    logging.info(f"Vault Path: {vault_path}")
    logging.info(f"MCP Path: {mcp_path}")
    
    chat = ObsidianChat(vault_path, mcp_path)
    await chat.chat_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Script failed: {e}")
        sys.exit(1) 