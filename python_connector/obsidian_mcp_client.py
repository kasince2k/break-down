import os
import json
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

class ObsidianMCPClient:
    def __init__(
        self,
        vault_paths: List[str],
        mcp_server_path: str,
        node_path: str = "node",
        config_dir: Optional[str] = None
    ):
        """
        Initialize the Obsidian MCP client.
        
        Args:
            vault_paths: List of paths to Obsidian vaults
            mcp_server_path: Path to the obsidian-mcp build/main.js file
            node_path: Path to Node.js executable (defaults to "node")
            config_dir: Optional custom config directory path
        """
        self.vault_paths = [str(Path(p).absolute()) for p in vault_paths]
        self.mcp_server_path = str(Path(mcp_server_path).absolute())
        self.node_path = node_path
        self.process: Optional[subprocess.Popen] = None
        
        # Set up config directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            if os.name == 'nt':  # Windows
                self.config_dir = Path(os.getenv('APPDATA')) / 'Claude'
            else:  # macOS/Linux
                self.config_dir = Path.home() / 'Library' / 'Application Support' / 'Claude'
        
        self.config_file = self.config_dir / 'claude_desktop_config.json'
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration"""
        self.logger = logging.getLogger('ObsidianMCP')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def update_config(self):
        """Update or create the Claude Desktop configuration file"""
        config: Dict[str, Any] = {
            "mcpServers": {
                "obsidian-local": {
                    "command": self.node_path,
                    "args": [
                        self.mcp_server_path,
                        *self.vault_paths
                    ]
                }
            }
        }
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Read existing config if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    existing_config = json.load(f)
                    # Update only the mcpServers section
                    existing_config["mcpServers"] = config["mcpServers"]
                    config = existing_config
            except json.JSONDecodeError:
                self.logger.warning("Existing config file is invalid, creating new one")
        
        # Write updated config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        self.logger.info(f"Updated configuration at {self.config_file}")

    def execute_tool(self, tool_name: str, params: Dict[str, Any], vault_name: str) -> Dict[str, Any]:
        """Execute an MCP tool and return the result"""
        if not self.process:
            raise RuntimeError("MCP server is not running")
            
        try:
            # Format the message
            message = {
                "type": "execute_tool",
                "tool": tool_name,
                "params": params,
                "vault": vault_name
            }
            
            # Send the message to the server's stdin
            self.process.stdin.write(json.dumps(message) + "\n")
            self.process.stdin.flush()
            
            # Read the response from stdout
            response = self.process.stdout.readline()
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"error": f"Invalid response from server: {response}"}
                
        except Exception as e:
            return {"error": f"Failed to execute tool: {str(e)}"}

    def start_server(self):
        """Start the Obsidian MCP server"""
        if self.process is not None:
            self.logger.warning("Server is already running")
            return
        
        try:
            self.update_config()
            
            # Start the server process with pipe communication
            self.process = subprocess.Popen(
                [self.node_path, self.mcp_server_path, *self.vault_paths],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            self.logger.info("Started Obsidian MCP server")
            
            # Log server output in background
            def log_output(pipe, is_stderr):
                for line in pipe:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                        
                    # Determine log level based on message content
                    if is_stderr and any(err in line.lower() for err in ['error', 'failed', 'exception']):
                        self.logger.error(f"Server: {line}")
                    elif any(warn in line.lower() for warn in ['warning', 'warn']):
                        self.logger.warning(f"Server: {line}")
                    else:
                        self.logger.info(f"Server: {line}")
            
            from threading import Thread
            Thread(target=log_output, args=(self.process.stdout, False), daemon=True).start()
            Thread(target=log_output, args=(self.process.stderr, True), daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise

    def stop_server(self):
        """Stop the Obsidian MCP server"""
        if self.process is None:
            self.logger.warning("Server is not running")
            return
        
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            self.logger.info("Stopped Obsidian MCP server")
        except subprocess.TimeoutExpired:
            self.logger.warning("Server did not terminate gracefully, forcing shutdown")
            self.process.kill()
            self.process = None
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_server()

# Example usage
if __name__ == "__main__":
    # Example paths - replace with your actual paths
    vault_path = "/Users/keshavag/projects/break-down-vault"
    mcp_path = "/Users/keshavag/projects/obsidian-mcp/build/main.js"
    
    # Using the client as a context manager
    with ObsidianMCPClient([vault_path], mcp_path) as client:
        input("Press Enter to stop the server...") 