# Obsidian Chat Assistant (Python Connector)

This directory contains a Python-based chat interface for interacting with an Obsidian vault using an AI assistant powered by the `autogen` framework and Anthropic's Claude models.

## Architecture: Plan-and-Execute

This assistant employs a **Plan-and-Execute** architecture for robust and predictable task handling:

1.  **Planner Agent:**
    *   An `autogen` `AssistantAgent` specifically configured with a system prompt instructing it to break down user requests into a sequence of clear, numbered steps.
    *   It **does not** have access to any tools. Its sole purpose is planning.
    *   It uses an Anthropic language model (configured via `.env`) to generate the plan.

2.  **Executor Agent:**
    *   Another `autogen` `AssistantAgent` responsible for executing individual steps provided by the Planner.
    *   It has access to tools provided by the Obsidian Meta Control Protocol (MCP) server.
    *   Its system prompt instructs it to focus on executing the *current* step accurately using the available tools.
    *   It also uses the configured Anthropic language model.

3.  **Execution Flow:**
    *   The user provides a request (e.g., "Create a note 'ideas', tag it #new, and read it").
    *   The `chat_loop` in `obsidian_chat.py` calls the `planner.run(task=user_input)` method.
    *   This method returns a `TaskResult` object containing the conversation history for the planning step.
    *   The `chat_loop` extracts the plan text from the `content` of the last message in the `TaskResult.messages` list.
    *   The plan text is parsed into individual, numbered steps.
    *   Each step (with numbering removed) is sent sequentially to the **Executor Agent** as a task using `executor.run_stream(task=step_text, ...)`.
    *   The output/result of each step is streamed to the console via `autogen_agentchat.ui.Console`.

## Key Components

*   **`obsidian_chat.py`**: The main script containing the `ObsidianChat` class, which orchestrates the setup and the chat loop implementing the Plan-and-Execute flow.
*   **Planner Agent (`self.planner`)**: Defined within `ObsidianChat`, configured for planning.
*   **Executor Agent (`self.executor`)**: Defined within `ObsidianChat`, configured for execution with MCP tools.
*   **Obsidian MCP Server**: This Python connector relies on an external Node.js server (from the `obsidian-mcp` project) running locally. This server provides the actual tools for interacting with the Obsidian vault(s). The path to its `main.js` build file must be configured.
*   **`autogen`**: The core multi-agent conversation framework used (`autogen-agentchat`, `autogen-core`).
*   **`autogen_ext`**: Custom extensions likely used for Anthropic model integration (`AnthropicChatCompletionClient`) and MCP tool loading (`mcp_server_tools`).
*   **`.env` File**: Used for configuration management.

## Setup & Configuration

1.  **Python Environment**: Ensure you have Python installed. Use a virtual environment manager like `venv` or `conda`. Dependencies are managed using `uv` (or `pip`).
2.  **Install Dependencies**: Install the required packages. If a `requirements.txt` exists, use:
    ```bash
    uv pip install -r requirements.txt
    # or pip install -r requirements.txt
    ```
    Key dependencies include `pyautogen`, `autogen-ext`, `python-dotenv`. You might need to install `pyautogen`, `autogen-ext`, `autogen-agentchat`, `json-schema-to-pydantic` individually if no `requirements.txt` is provided.
3.  **Obsidian MCP Server**:
    *   Clone the `obsidian-mcp` repository separately.
    *   Follow its instructions to build the server (`npm install`, `npm run build`).
    *   Note the absolute path to the generated `build/main.js` file.
4.  **`.env` File**: Create a `.env` file in the root directory (`break-down/`) with the following variables:
    ```dotenv
    # API key for Anthropic API
    ANTHROPIC_API_KEY="sk-ant-..."
    # Anthropic model name (e.g., claude-3-haiku-20240307, claude-3-sonnet-...)
    ANTHROPIC_MODEL="claude-3-haiku-20240307"
    # Absolute path to your Obsidian vault
    VAULT_PATH="/path/to/your/obsidian/vault"
    # Absolute path to the obsidian-mcp build file
    MCP_PATH="/path/to/obsidian-mcp/build/main.js"
    ```

## How to Run

Navigate to the root directory (`break-down/`) in your terminal and run:

```bash
python python-connector/obsidian_chat.py
```

Follow the prompts in the console to interact with the assistant. Use commands like `/help` and `/quit`.

## Notes

*   The current implementation assumes `planner.run()` returns a `TaskResult` object with a specific structure (`.messages[-1].content`). Compatibility may vary slightly between different `autogen` versions.
*   Error handling is basic; failed steps currently stop the execution of the rest of the plan for that request.
