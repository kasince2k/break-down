# Obsidian Article Breakdown Agent

This agent uses the Agent Development Kit (ADK) to create structured breakdowns of articles in Obsidian, following a specific workflow to organize content and create visual canvas representations.

## Overview

The Obsidian Article Breakdown Agent helps users organize and structure articles in their Obsidian vault. It follows a systematic workflow to:

1. Identify the article in the Obsidian vault
2. Create a structured folder for the breakdown
3. Analyze the content and create a hierarchical breakdown
4. Generate markdown files for each section and subsection
5. Build a visual canvas representation with proper layout and connections

For a detailed explanation of the agent's architecture and workflow, see the [Architecture Document](architecture.md).

## Features

- Automatic article content analysis and structure detection
- Creation of hierarchical markdown files with proper linking
- YAML frontmatter with metadata for each file
- Visual canvas representation with color-coded nodes
- Support for articles of different lengths and complexities

## Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/get-started/quickstart/)
- Access to Gemini API or Vertex AI
- Obsidian vault with the obsidian-mcp server configured

## Installation

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd obsidian-article-breakdown
   ```

2. Run the setup script to install dependencies and configure the agent:

   ```bash
   python setup.py
   ```

   This script will:
   - Check if you have the required Python version
   - Verify that Poetry is installed
   - Install dependencies using Poetry
   - Create a `.env` file from the template
   - Help you locate your Obsidian vault

   Alternatively, you can perform these steps manually:

   ```bash
   poetry install
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

## Usage

### Setting Up the MCP Server

Before running the agent, you need to set up the Obsidian MCP server that provides the tools for interacting with your Obsidian vault:

1. Make sure you have an Obsidian vault set up on your system.

2. You can start the MCP server separately:

   ```bash
   python obsidian_mcp_server.py --vault-path /path/to/your/obsidian/vault
   ```

   Or let the run script handle it for you (see below).

### Running the Agent

The easiest way to run the agent is using the provided run scripts, which will start both the MCP server and the agent:

#### On Linux/macOS

```bash
# Make the script executable
chmod +x run.sh

# Run the agent with the CLI interface
./run.sh --vault-path /path/to/your/obsidian/vault

# Or run with the web UI
./run.sh --vault-path /path/to/your/obsidian/vault --web
```

#### On Windows

```batch
# Run the agent with the CLI interface
run.bat --vault-path "C:\path\to\your\obsidian\vault"

# Or run with the web UI
run.bat --vault-path "C:\path\to\your\obsidian\vault" --web
```

You can also run the Python script directly:

```bash
# Activate the Poetry environment
poetry shell

# Run the agent with the CLI interface
python run_agent.py --vault-path /path/to/your/obsidian/vault

# Or run with the web UI
python run_agent.py --vault-path /path/to/your/obsidian/vault --web-ui
```

Alternatively, you can run the agent manually:

1. Start the MCP server as described above.

2. Activate the Poetry environment:

   ```bash
   poetry shell
   ```

3. Run the agent using the ADK CLI:

   ```bash
   adk run .
   ```

   Or use the ADK Dev UI:

   ```bash
   adk web
   ```

4. Interact with the agent by sending a message with "Obsidian Mode" and the path to the article:

   ```
   Obsidian Mode
   Please create a breakdown for the article at path: Clippings/example-article.md
   ```

### Example Interaction

```
User: Obsidian Mode
      Please create a breakdown for the article at path: Clippings/sample-article.md

Agent: Article breakdown complete!

      Created breakdown folder: Understanding Markdown-Breakdown
      Generated 12 markdown files
      Created canvas visualization: Understanding Markdown-Breakdown/Understanding Markdown-Breakdown.canvas

      You can now open the canvas file in Obsidian to view the structured breakdown.
```

### Example Files

The `examples` directory contains sample files you can use to test the agent:

- `sample-article.md`: A comprehensive guide to Markdown that you can use to test the agent
- See the [examples README](examples/README.md) for more information on how to use these files

## Configuration

The agent behavior can be customized by modifying the following files:

- `obsidian_article_breakdown/prompt.py`: Contains the system prompt and templates
- `obsidian_article_breakdown/agent.py`: Contains the agent implementation

## MCP Server

The agent uses a Model Context Protocol (MCP) server to interact with your Obsidian vault. The server provides the following tools:

- `read_file`: Reads file content from the Obsidian vault
- `write_file`: Writes content to a file in the Obsidian vault
- `create_folder`: Creates a folder in the Obsidian vault
- `list_files`: Lists files in a folder in the Obsidian vault
- `search_vault`: Searches for content in the Obsidian vault

For more details on the MCP server, see [MCP_SERVER_README.md](MCP_SERVER_README.md).

## File Structure

The agent creates the following file structure for each article breakdown:

```
[ArticleTitle]-Breakdown/
├── 00-Summary.md
├── 01-[MainSection].md
├── 01.01-[Subsection].md
├── 01.02-[Subsection].md
├── 02-[MainSection].md
├── ...
├── Key-Concepts.md (optional)
├── References.md (optional)
└── [ArticleTitle]-Breakdown.canvas
```

## Canvas Visualization

The agent creates a canvas file with the following structure:

- Original article at the top (0,-600)
- Summary node below the original (0,-300)
- Level 1 nodes (main sections) arranged horizontally at y=0
- Level 2 nodes (subsections) below their respective parents at y=300
- Special nodes positioned to the right of the main structure

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
