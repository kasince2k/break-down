#!/usr/bin/env python3
"""
Obsidian MCP Server

This script implements a Model Context Protocol (MCP) server for interacting with Obsidian.
It provides tools for reading and writing files, creating folders, and searching the vault.

Usage:
    python obsidian_mcp_server.py --vault-path /path/to/obsidian/vault --port 8000
"""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse


class ObsidianMcpServer:
    """MCP server for interacting with Obsidian."""

    def __init__(self, vault_path: str):
        """Initialize the server.

        Args:
            vault_path: Path to the Obsidian vault.
        """
        self.vault_path = os.path.abspath(vault_path)
        self.config = self._load_config()

        # Validate vault path
        if not os.path.isdir(self.vault_path):
            raise ValueError(f"Vault path does not exist or is not a directory: {self.vault_path}")

        print(f"Obsidian MCP Server initialized with vault path: {self.vault_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Load the server configuration.

        Returns:
            The server configuration.
        """
        config_path = os.path.join(os.path.dirname(__file__), "obsidian-mcp-config.json")
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return {
                "name": "obsidian-mcp",
                "description": "MCP server for interacting with Obsidian",
                "version": "1.0.0",
                "tools": [],
                "resources": [],
            }

    def get_server_info(self) -> Dict[str, Any]:
        """Get information about the server.

        Returns:
            Server information.
        """
        return {
            "name": self.config.get("name", "obsidian-mcp"),
            "description": self.config.get(
                "description", "MCP server for interacting with Obsidian"
            ),
            "version": self.config.get("version", "1.0.0"),
            "tools": [
                {
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "input_schema": tool.get("input_schema"),
                    "output_schema": tool.get("output_schema"),
                }
                for tool in self.config.get("tools", [])
            ],
            "resources": [
                {
                    "name": resource.get("name"),
                    "description": resource.get("description"),
                    "uri": resource.get("uri"),
                }
                for resource in self.config.get("resources", [])
            ],
        }

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.

        Returns:
            Tool execution result.
        """
        # Find the tool
        tool = next((t for t in self.config.get("tools", []) if t.get("name") == tool_name), None)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}

        # Validate arguments
        required_args = tool.get("input_schema", {}).get("required", [])
        for arg in required_args:
            if arg not in arguments:
                return {"error": f"Missing required argument: {arg}"}

        # Execute the tool
        try:
            if tool_name == "read_file":
                return self._read_file(arguments.get("path"))
            elif tool_name == "write_file":
                return self._write_file(arguments.get("path"), arguments.get("content"))
            elif tool_name == "create_folder":
                return self._create_folder(arguments.get("path"))
            elif tool_name == "list_files":
                return self._list_files(arguments.get("path"), arguments.get("recursive", False))
            elif tool_name == "search_vault":
                return self._search_vault(arguments.get("query"), arguments.get("path", "/"))
            else:
                return {"error": f"Tool not implemented: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def access_resource(self, uri: str) -> Dict[str, Any]:
        """Access a resource.

        Args:
            uri: Resource URI.

        Returns:
            Resource data.
        """
        # Find the resource
        resource = next((r for r in self.config.get("resources", []) if r.get("uri") == uri), None)
        if not resource:
            return {"error": f"Resource not found: {uri}"}

        # Access the resource
        try:
            if uri == "obsidian://vault-info":
                return self._get_vault_info()
            elif uri == "obsidian://vault-config":
                return self._get_vault_config()
            else:
                return {"error": f"Resource not implemented: {uri}"}
        except Exception as e:
            return {"error": str(e)}

    def _read_file(self, path: str) -> Dict[str, Any]:
        """Read a file from the Obsidian vault.

        Args:
            path: Path to the file in the Obsidian vault.

        Returns:
            File content.
        """
        full_path = os.path.join(self.vault_path, path)
        if not os.path.isfile(full_path):
            return {"error": f"File not found: {path}"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file in the Obsidian vault.

        Args:
            path: Path to the file in the Obsidian vault.
            content: Content to write to the file.

        Returns:
            Success status.
        """
        full_path = os.path.join(self.vault_path, path)

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True}
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}

    def _create_folder(self, path: str) -> Dict[str, Any]:
        """Create a folder in the Obsidian vault.

        Args:
            path: Path to the folder in the Obsidian vault.

        Returns:
            Success status.
        """
        full_path = os.path.join(self.vault_path, path)

        try:
            os.makedirs(full_path, exist_ok=True)
            return {"success": True}
        except Exception as e:
            return {"error": f"Error creating folder: {str(e)}"}

    def _list_files(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """List files in a folder in the Obsidian vault.

        Args:
            path: Path to the folder in the Obsidian vault.
            recursive: Whether to list files recursively.

        Returns:
            List of file paths.
        """
        full_path = os.path.join(self.vault_path, path)
        if not os.path.isdir(full_path):
            return {"error": f"Folder not found: {path}"}

        try:
            if recursive:
                files = []
                for root, _, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, self.vault_path)
                        files.append(rel_path)
            else:
                files = [
                    os.path.join(path, f)
                    for f in os.listdir(full_path)
                    if os.path.isfile(os.path.join(full_path, f))
                ]

            return {"files": files}
        except Exception as e:
            return {"error": f"Error listing files: {str(e)}"}

    def _search_vault(self, query: str, path: str = "/") -> Dict[str, Any]:
        """Search for files in the Obsidian vault.

        Args:
            query: Search query.
            path: Path to search in.

        Returns:
            Search results.
        """
        full_path = os.path.join(self.vault_path, path.lstrip("/"))
        if not os.path.isdir(full_path):
            return {"error": f"Folder not found: {path}"}

        try:
            results = []
            for root, _, filenames in os.walk(full_path):
                for filename in filenames:
                    if not filename.endswith((".md", ".txt")):
                        continue

                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.vault_path)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        if query.lower() in content.lower():
                            # Find a snippet containing the query
                            index = content.lower().find(query.lower())
                            start = max(0, index - 50)
                            end = min(len(content), index + len(query) + 50)
                            snippet = content[start:end]

                            results.append({"path": rel_path, "snippet": snippet})
                    except Exception:
                        # Skip files that can't be read
                        pass

            return {"results": results}
        except Exception as e:
            return {"error": f"Error searching vault: {str(e)}"}

    def _get_vault_info(self) -> Dict[str, Any]:
        """Get information about the Obsidian vault.

        Returns:
            Vault information.
        """
        try:
            # Count files by type
            file_counts = {"markdown": 0, "canvas": 0, "other": 0}
            total_files = 0

            for root, _, filenames in os.walk(self.vault_path):
                for filename in filenames:
                    total_files += 1
                    if filename.endswith(".md"):
                        file_counts["markdown"] += 1
                    elif filename.endswith(".canvas"):
                        file_counts["canvas"] += 1
                    else:
                        file_counts["other"] += 1

            return {
                "vault_path": self.vault_path,
                "vault_name": os.path.basename(self.vault_path),
                "total_files": total_files,
                "file_counts": file_counts,
            }
        except Exception as e:
            return {"error": f"Error getting vault info: {str(e)}"}

    def _get_vault_config(self) -> Dict[str, Any]:
        """Get configuration of the Obsidian vault.

        Returns:
            Vault configuration.
        """
        config_path = os.path.join(self.vault_path, ".obsidian", "app.json")
        if not os.path.isfile(config_path):
            return {"error": "Vault configuration not found"}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return {"config": config}
        except Exception as e:
            return {"error": f"Error getting vault configuration: {str(e)}"}


class McpRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the MCP server."""

    def __init__(self, *args, **kwargs):
        """Initialize the request handler."""
        self.server_instance = kwargs.pop("server_instance", None)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/":
            # Return server info
            self._send_json_response(200, self.server_instance.get_server_info())
        elif parsed_url.path == "/resource":
            # Access a resource
            query_params = parse_qs(parsed_url.query)
            uri = query_params.get("uri", [""])[0]

            if not uri:
                self._send_json_response(400, {"error": "Missing resource URI"})
                return

            result = self.server_instance.access_resource(uri)
            if "error" in result:
                self._send_json_response(404, result)
            else:
                self._send_json_response(200, result)
        else:
            self._send_json_response(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/tool":
            # Execute a tool
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json_response(400, {"error": "Empty request body"})
                return

            try:
                request_body = self.rfile.read(content_length).decode("utf-8")
                request_data = json.loads(request_body)

                tool_name = request_data.get("tool_name")
                arguments = request_data.get("arguments", {})

                if not tool_name:
                    self._send_json_response(400, {"error": "Missing tool name"})
                    return

                result = self.server_instance.execute_tool(tool_name, arguments)
                if "error" in result:
                    self._send_json_response(400, result)
                else:
                    self._send_json_response(200, result)
            except json.JSONDecodeError:
                self._send_json_response(400, {"error": "Invalid JSON"})
            except Exception as e:
                self._send_json_response(500, {"error": str(e)})
        else:
            self._send_json_response(404, {"error": "Not found"})

    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send a JSON response.

        Args:
            status_code: HTTP status code.
            data: Response data.
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = json.dumps(data, indent=2).encode("utf-8")
        self.wfile.write(response)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Obsidian MCP Server")
    parser.add_argument(
        "--vault-path",
        type=str,
        required=True,
        help="Path to the Obsidian vault",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to",
    )
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()

    try:
        # Create the server instance
        server_instance = ObsidianMcpServer(args.vault_path)

        # Create a custom request handler with the server instance
        def handler(*handler_args, **handler_kwargs):
            return McpRequestHandler(
                *handler_args, server_instance=server_instance, **handler_kwargs
            )

        # Create and start the HTTP server
        server = HTTPServer((args.host, args.port), handler)
        print(f"Obsidian MCP Server running at http://{args.host}:{args.port}")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
        finally:
            server.server_close()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
