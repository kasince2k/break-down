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
    def __init__(self, vault_path: str, mcp_path: str, planner_prompt: str, executor_prompt: str):
        self.vault_path = vault_path
        self.mcp_path = mcp_path
        self.planner_prompt = planner_prompt
        self.executor_prompt = executor_prompt
        self.planner = None
        self.executor = None

    async def setup(self):
        model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        model_client = AnthropicChatCompletionClient(model=model_name)

        # Load tools from MCP
        server = StdioServerParams(command="node", args=[self.mcp_path, self.vault_path])
        tools = await mcp_server_tools(server)

        # Setup planner
        self.planner = AssistantAgent(
            name="planner",
            model_client=model_client,
            tools=[],
            system_message=self.planner_prompt
        )

        # Setup executor
        self.executor = AssistantAgent(
            name="executor",
            model_client=model_client,
            tools=tools,
            system_message=self.executor_prompt,
            model_client_stream=True,
            reflect_on_tool_use=False
        )

    async def chat_loop(self):
        print("\n=== Obsidian Chat Assistant ===")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "/quit":
                print("Goodbye!")
                break

            # Optional article content
            article_path = Path(self.vault_path) / f"Clippings/{user_input}.md"
            article_content = ""
            if article_path.exists():
                with open(article_path, 'r', encoding='utf-8') as f:
                    article_content = f.read()
                task_for_planner = f"User request: Break down article Clippings/{user_input}.md\n\nArticle Content:\n{article_content}"
            else:
                task_for_planner = user_input

            try:
                plan_result = await self.planner.run(task=task_for_planner)
                plan_text = plan_result.messages[-1].content.strip()
                print("\nPlan:\n" + plan_text)
            except Exception as e:
                logging.error(f"[Planner Error] {e}")
                continue

            steps = [line.strip() for line in plan_text.splitlines() if line.strip() and line.strip()[0].isdigit()]

            for i, step in enumerate(steps):
                try:
                    step_text = step.split('.', 1)[-1].strip()
                    logging.info(f"[Executor] Step {i+1}: {step_text}")

                    task = step_text
                    if article_content and any(word in step_text.lower() for word in ["summary", "section", "subsection"]):
                        task += f"\n\nUse this content:\n{article_content}\n\nOriginal article path for linking: Clippings/{user_input}.md"
                    elif article_content and "canvas" in step_text.lower():
                        task += f"\n\nOriginal article path for canvas node: Clippings/{user_input}.md"

                    logging.info(f"Task for executor (first 200 chars): {str(task)[:200]}")

                    if step_text.lower().startswith("create directory"):
                        async for response in self.executor.run_stream(task=task, cancellation_token=CancellationToken()):
                            logging.debug(f"[Stream] {type(response)} - {str(response)[:150]}")
                    else:
                        await Console(
                            self.executor.run_stream(task=task, cancellation_token=CancellationToken())
                        )
                except Exception as e:
                    logging.error(f"[Executor Error] Step failed: {e}")
                    break

async def main():
    load_dotenv()

    vault_path = os.getenv("VAULT_PATH")
    mcp_path = os.getenv("MCP_PATH")
    
    # Correct paths relative to this script file
    script_dir = Path(__file__).parent
    planner_file = script_dir / "planner-prompt.md"
    executor_file = script_dir / "executor-prompt.md"

    if not vault_path or not mcp_path:
        raise ValueError("VAULT_PATH or MCP_PATH not set in environment")
    
    # Check if prompt files exist at the corrected path
    if not planner_file.is_file():
        raise FileNotFoundError(f"Planner prompt file not found at: {planner_file}")
    if not executor_file.is_file():
        raise FileNotFoundError(f"Executor prompt file not found at: {executor_file}")

    with open(planner_file, 'r') as f:
        planner_prompt = f.read()
    with open(executor_file, 'r') as f:
        executor_prompt = f.read()

    chat = ObsidianChat(vault_path, mcp_path, planner_prompt, executor_prompt)
    await chat.setup()
    await chat.chat_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Fatal exception: {e}")
        sys.exit(1)
