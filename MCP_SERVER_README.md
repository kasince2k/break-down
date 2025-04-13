# Obsidian MCP Server

This is a Model Context Protocol (MCP) server for interacting with Obsidian. It provides tools for reading and writing files, creating folders, and searching the vault.

## Overview

The Obsidian MCP Server allows ADK agents to interact with an Obsidian vault. It implements the Model Context Protocol (MCP) to provide a standardized interface for tools and resources.

## Features

- Read and write files in the Obsidian vault
- Create folders in the Obsidian vault
- List files in the vault
- Search for content in the vault
- Access vault information and configuration

## Prerequisites

- Python 3.9+
- An Obsidian vault

## Installation

No additional installation is required beyond the dependencies for the Obsidian Article Breakdown Agent.

## Usage

### Starting the Server

1. Run the server script with the path to your Obsidian vault:

```bash
python obsidian_mcp_server.py --vault-path /path/to/your/obsidian/vault
```

2. By default, the server runs on `localhost:8000`. You can specify a different host and port:

```bash
python obsidian_mcp_server.py --vault-path /path/to/your/obsidian/vault --host 0.0.0.0 --port 8080
```

### Configuring the Agent to Use the Server

1. Update your `.env` file with the MCP server URL:

```
MCP_SERVER_URL=http://localhost:8000
```

2. The agent is already configured to use the `obsidian-mcp` server name.

## Available Tools

The server provides the following tools:

### read_file

Read a file from the Obsidian vault.

**Input:**
- `path`: Path to the file in the Obsidian vault

**Output:**
- `content`: Content of the file

### write_file

Write content to a file in the Obsidian vault.

**Input:**
- `path`: Path to the file in the Obsidian vault
- `content`: Content to write to the file

**Output:**
- `success`: Whether the file was written successfully

### create_folder

Create a folder in the Obsidian vault.

**Input:**
- `path`: Path to the folder in the Obsidian vault

**Output:**
- `success`: Whether the folder was created successfully

### list_files

List files in a folder in the Obsidian vault.

**Input:**
- `path`: Path to the folder in the Obsidian vault
- `recursive` (optional): Whether to list files recursively (default: false)

**Output:**
- `files`: List of file paths

### search_vault

Search for files in the Obsidian vault.

**Input:**
- `query`: Search query
- `path` (optional): Path to search in (default: "/")

**Output:**
- `results`: List of search results, each containing:
  - `path`: Path to the file
  - `snippet`: Snippet of the file content containing the match

## Available Resources

The server provides the following resources:

### vault_info

Information about the Obsidian vault.

**URI:** `obsidian://vault-info`

**Output:**
- `vault_path`: Path to the vault
- `vault_name`: Name of the vault
- `total_files`: Total number of files in the vault
- `file_counts`: Counts of files by type

### vault_config

Configuration of the Obsidian vault.

**URI:** `obsidian://vault-config`

**Output:**
- `config`: Vault configuration

## API Endpoints

The server exposes the following HTTP endpoints:

- `GET /`: Get server information
- `GET /resource?uri=<uri>`: Access a resource
- `POST /tool`: Execute a tool

## Customization

You can customize the server by modifying the `obsidian-mcp-config.json` file. This file defines the tools and resources provided by the server.

## Troubleshooting

- If you encounter permission errors, make sure the server has read and write access to the Obsidian vault.
- If the server can't find the vault, check that the path is correct and absolute.
- If tools fail to execute, check the server logs for error messages.

## License

[MIT License](LICENSE)
