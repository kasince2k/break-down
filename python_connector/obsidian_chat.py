import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ObsidianChat:
    def __init__(self, vault_path: str, mcp_path: str, planner_system_prompt: str, executor_system_prompt: str):
        self.vault_path = vault_path
        self.mcp_path = mcp_path
        self.planner_system_prompt = planner_system_prompt
        self.executor_system_prompt = executor_system_prompt
        self.planner = None
        self.executor = None
        self.tools = None # To store loaded tools after setup

    async def setup(self):
        """Initializes MCP tools and sets up agents. Should be called once."""
        if self.planner and self.executor: # Prevent re-initialization
            logging.warning("Agents already initialized.")
            return

        try:
            # --- Load MCP Tools --- 
            logging.info("Initializing MCP server and tools...")
            obsidian_mcp_server = StdioServerParams(
                command="node",
                args=[self.mcp_path, self.vault_path]
            )
            self.tools = await mcp_server_tools(obsidian_mcp_server)
            logging.info("MCP tools initialized successfully!")

            # --- Common Setup ---
            model_name = os.getenv("ANTHROPIC_MODEL") 
            logging.info(f"Using model: {model_name}")
            model_client = AnthropicChatCompletionClient(model=model_name)

            # --- Planner Setup ---
            logging.info(f"Planner System Prompt (start): {self.planner_system_prompt[:200]}...")
            self.planner = AssistantAgent(
                name="planner",
                model_client=model_client,
                system_message=self.planner_system_prompt,
                tools=[], 
            )
            logging.info("Planner agent initialized successfully!")

            # --- Executor Setup ---
            logging.info(f"Executor System Prompt (start): {self.executor_system_prompt[:200]}...")
            self.executor = AssistantAgent(
                name="obsidian_executor",
                model_client=model_client,
                tools=self.tools, # Use stored tools
                system_message=self.executor_system_prompt, 
                reflect_on_tool_use=False,
                model_client_stream=True, # Stream might still be useful for logging tool calls
            )
            logging.info("Executor agent initialized successfully!")
            
        except Exception as e:
            logging.error(f"Error during agent setup: {str(e)}")
            raise

    async def process_article_breakdown(self, filename_without_ext: str):
        """Processes a single article breakdown request."""
        if not self.planner or not self.executor:
            logging.error("Agents not initialized. Call setup() first.")
            raise RuntimeError("Agents not initialized.")

        logging.info(f"--- Starting breakdown process for: {filename_without_ext} ---")
        
        # --- Python Pre-processing: Read Article --- 
        article_content: str | None = None
        original_article_path: str | None = None 
        full_article_path: Path | None = None 
        task_for_planner: str | None = None

        try:
            # Construct paths
            original_article_path = f"Clippings/{filename_without_ext}.md"
            full_article_path = Path(self.vault_path) / original_article_path
            logging.info(f"Target article path: {full_article_path}")

            if not full_article_path.is_file():
                logging.error(f"Article file not found: {full_article_path}")
                raise FileNotFoundError(f"Article file not found: {full_article_path}")

            # Read content
            logging.info(f"Reading article content from: {full_article_path}")
            with open(full_article_path, 'r', encoding='utf-8') as f:
                article_content = f.read()
            logging.info(f"Successfully read article content ({len(article_content)} chars).")
            
            # Construct planner task including content
            generic_request = f"Break down the article located at {original_article_path}"
            task_for_planner = f"User request: {generic_request}\n\nArticle Content:\n{article_content}"
        
        except Exception as e:
            logging.error(f"Error during pre-processing/reading file '{original_article_path or filename_without_ext}': {e}")
            raise # Re-raise to signal failure

        # --- Plan Step --- 
        logging.info("[Planner] Generating plan...")
        plan_text = None
        try:
            plan_result = await self.planner.run(task=task_for_planner)
            if not hasattr(plan_result, 'messages') or not plan_result.messages:
                raise ValueError("Planner run did not return messages in TaskResult.")
            last_message = plan_result.messages[-1]
            if not hasattr(last_message, 'content') or not last_message.content:
                raise ValueError("Planner message content is missing or empty.")
            plan_text = last_message.content.strip()
            if not plan_text:
                 raise ValueError("Planner returned an empty plan string.")
            logging.info(f"Generated Plan:\n{plan_text}")
        except Exception as e:
            logging.error(f"Error generating plan: {e}")
            raise # Re-raise to signal failure

        # --- Execute Plan (with context injection) --- 
        plan_steps = [s.strip() for s in plan_text.split('\n') if s.strip() and s.strip()[0].isdigit()]
        
        if not plan_steps:
             logging.warning("No valid steps parsed from plan. Skipping execution.")
             return # Or raise error? For now, just return.

        logging.info(f"Executing {len(plan_steps)} plan steps...")
        for i, step in enumerate(plan_steps):
            step_text = step.split('.', 1)[-1].strip() 
            logging.info(f"[Executor] Processing step {i+1}/{len(plan_steps)}: {step_text}")
            
            # Modify create steps to include content
            task_for_executor = step_text
            if step_text.lower().startswith("create directory"):
                async for response in self.executor.run_stream(task=task_for_executor, cancellation_token=CancellationToken()):
                    logging.debug(f"Executor stream response chunk: {str(response)[:150]}")
                    pass # Consume stream
            elif step_text.lower().startswith("create summary file") or step_text.lower().startswith("create section file") or step_text.lower().startswith("create subsection file"):
                if article_content:
                    task_for_executor = f"{step_text}. Use this content:\n\n{article_content}"
                    if original_article_path:
                        task_for_executor += f"\nOriginal article path for linking: {original_article_path}"
                else:
                    logging.error(f"CRITICAL ERROR: Article content is missing for step '{step_text}'. Skipping.")
                    continue 
            elif step_text.lower().startswith("create canvas"):
                if original_article_path:
                    task_for_executor += f"\nOriginal article path for canvas node: {original_article_path}"

            # Execute step - NO Console wrapper
            try:
                # Log start of task safely
                try:
                    task_snippet = str(task_for_executor)[:200]
                except Exception as log_e:
                    task_snippet = f"<logging error: {log_e}>"
                logging.info(f"Passing task to executor: '{task_snippet}...'") 
                
                # Use run() instead of run_stream for programmatic execution?
                # Or consume run_stream without Console
                logging.debug("Executing step via run_stream (consuming stream)")
                async for response in self.executor.run_stream(task=task_for_executor, cancellation_token=CancellationToken()):
                     logging.debug(f"Executor stream response chunk: {str(response)[:150]}")
                     pass # Consume stream
                logging.info(f"Finished executing step {i+1}.")

            except Exception as e:
                logging.error(f"Error executing step '{step_text}': {e}")
                logging.info("Stopping plan execution due to error.")
                raise # Re-raise to signal failure to the caller
        
        logging.info(f"--- Finished breakdown process for: {filename_without_ext} ---")

# Renamed main to be the importable entry point
async def run_breakdown_for_file(filename_without_ext: str):
    """Sets up and runs the article breakdown process for a single file."""
    load_dotenv()
    
    # --- Load Config and System Prompts --- 
    vault_path = os.getenv("VAULT_PATH")
    mcp_path = os.getenv("MCP_PATH")
    
    script_dir = Path(__file__).parent
    planner_file = script_dir / "planner-prompt.md"
    executor_file = script_dir / "executor-prompt.md"

    if not vault_path or not mcp_path:
        raise ValueError("VAULT_PATH or MCP_PATH not set in environment")
    
    if not planner_file.is_file():
        raise FileNotFoundError(f"Planner prompt file not found at: {planner_file}")
    if not executor_file.is_file():
        raise FileNotFoundError(f"Executor prompt file not found at: {executor_file}")

    try:
        with open(planner_file, 'r') as f:
            planner_system_prompt = f.read()
        with open(executor_file, 'r') as f:
            executor_system_prompt = f.read()
        logging.info("Loaded prompts successfully.")
    except Exception as e:
        logging.error(f"Failed to read prompt file(s): {e}")
        raise

    logging.info(f"Vault Path: {vault_path}")
    logging.info(f"MCP Path: {mcp_path}")
    
    # Create and setup the chat instance
    chat = ObsidianChat(vault_path, mcp_path, planner_system_prompt, executor_system_prompt)
    await chat.setup()
    
    # Process the specific file
    logging.info(f"Calling process_article_breakdown for: {filename_without_ext}")
    await chat.process_article_breakdown(filename_without_ext)


if __name__ == "__main__":
    # This block is now primarily for direct testing if needed.
    # You would typically run vault_monitor.py instead.
    logging.warning("Running obsidian_chat.py directly for testing.")
    
    # Example usage for direct testing:
    test_filename = "example_article" # CHANGE THIS to your test filename without .md
    logging.info(f"Starting direct test run for: {test_filename}")
    
    try:
        asyncio.run(run_breakdown_for_file(test_filename))
        logging.info(f"Direct test run for '{test_filename}' completed.")
    except Exception as e:
        logging.error(f"Direct test run failed: {e}")
        sys.exit(1)
