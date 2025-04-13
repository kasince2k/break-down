#!/usr/bin/env python3
"""
Run script for the Obsidian Article Breakdown Agent.

This script starts the Obsidian MCP Server and runs the agent.
"""

import argparse
import os
import subprocess
import sys
import time
from typing import Optional

# Check if the required packages are installed
try:
    from google.adk import Agent
    from google.adk.run import run_agent
except ImportError:
    print("Error: Required packages not found. Please install the Agent Development Kit (ADK).")
    print("Run: pip install google-adk")
    sys.exit(1)

# Import the agent
try:
    from obsidian_article_breakdown import ObsidianArticleBreakdownAgent
except ImportError:
    print("Error: Obsidian Article Breakdown Agent not found.")
    print("Make sure you're running this script from the correct directory.")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Obsidian Article Breakdown Agent")
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
        help="Port for the MCP server",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for the MCP server",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Don't start the MCP server (use if it's already running)",
    )
    parser.add_argument(
        "--web-ui",
        action="store_true",
        help="Run the agent with the ADK web UI",
    )
    return parser.parse_args()


def start_mcp_server(vault_path: str, host: str, port: int) -> Optional[subprocess.Popen]:
    """Start the Obsidian MCP Server.

    Args:
        vault_path: Path to the Obsidian vault.
        host: Host to bind to.
        port: Port to listen on.

    Returns:
        The server process or None if it couldn't be started.
    """
    server_script = os.path.join(os.path.dirname(__file__), "obsidian_mcp_server.py")

    if not os.path.isfile(server_script):
        print(f"Error: MCP server script not found: {server_script}")
        return None

    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            [
                sys.executable,
                server_script,
                "--vault-path",
                vault_path,
                "--host",
                host,
                "--port",
                str(port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for the server to start
        print("Starting Obsidian MCP Server...")
        time.sleep(2)

        # Check if the server is running
        if process.poll() is not None:
            # Server exited
            stdout, stderr = process.communicate()
            print(f"Error starting MCP server: {stderr}")
            return None

        print(f"Obsidian MCP Server running at http://{host}:{port}")
        return process
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}")
        return None


def run_agent_cli(agent: Agent) -> None:
    """Run the agent using the ADK CLI.

    Args:
        agent: The agent to run.
    """
    try:
        run_agent(agent)
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Error running agent: {str(e)}")


def run_agent_web_ui() -> None:
    """Run the agent using the ADK web UI."""
    try:
        # Run the ADK web UI
        subprocess.run([sys.executable, "-m", "google.adk.web"], check=True)
    except KeyboardInterrupt:
        print("\nWeb UI stopped by user")
    except Exception as e:
        print(f"Error running web UI: {str(e)}")


def main() -> None:
    """Main function."""
    args = parse_args()

    # Set environment variables for the MCP server
    os.environ["MCP_SERVER_URL"] = f"http://{args.host}:{args.port}"

    # Start the MCP server if needed
    server_process = None
    if not args.no_server:
        server_process = start_mcp_server(args.vault_path, args.host, args.port)
        if not server_process:
            print("Failed to start MCP server. Exiting.")
            sys.exit(1)

    try:
        # Run the agent
        if args.web_ui:
            run_agent_web_ui()
        else:
            agent = ObsidianArticleBreakdownAgent()
            run_agent_cli(agent)
    finally:
        # Stop the MCP server if it was started
        if server_process:
            print("Stopping Obsidian MCP Server...")
            server_process.terminate()
            server_process.wait()


if __name__ == "__main__":
    main()
