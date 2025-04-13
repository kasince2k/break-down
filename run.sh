#!/bin/bash
# Run script for the Obsidian Article Breakdown Agent

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3.9 or higher."
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is required but not found."
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Function to display help
show_help() {
    echo "Usage: ./run.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -v, --vault-path PATH      Path to the Obsidian vault (required)"
    echo "  -p, --port PORT            Port for the MCP server (default: 8000)"
    echo "  -H, --host HOST            Host for the MCP server (default: localhost)"
    echo "  -w, --web                  Run with the ADK web UI"
    echo "  -n, --no-server            Don't start the MCP server (use if it's already running)"
    echo "  -s, --setup                Run the setup script before starting"
    echo ""
    echo "Example:"
    echo "  ./run.sh --vault-path ~/Documents/Obsidian/MyVault --web"
    echo ""
}

# Default values
VAULT_PATH=""
PORT=8000
HOST="localhost"
WEB=false
NO_SERVER=false
SETUP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--vault-path)
            VAULT_PATH="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -H|--host)
            HOST="$2"
            shift 2
            ;;
        -w|--web)
            WEB=true
            shift
            ;;
        -n|--no-server)
            NO_SERVER=true
            shift
            ;;
        -s|--setup)
            SETUP=true
            shift
            ;;
        *)
            echo "Error: Unknown option $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if vault path is provided
if [ -z "$VAULT_PATH" ]; then
    echo "Error: Vault path is required."
    show_help
    exit 1
fi

# Run setup if requested
if [ "$SETUP" = true ]; then
    echo "Running setup script..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "Setup failed. Exiting."
        exit 1
    fi
fi

# Activate Poetry environment
echo "Activating Poetry environment..."
poetry install

# Build the command
CMD="poetry run python run_agent.py --vault-path \"$VAULT_PATH\" --port $PORT --host $HOST"

if [ "$NO_SERVER" = true ]; then
    CMD="$CMD --no-server"
fi

if [ "$WEB" = true ]; then
    CMD="$CMD --web-ui"
fi

# Run the agent
echo "Running Obsidian Article Breakdown Agent..."
echo "Vault path: $VAULT_PATH"
echo "MCP server: $HOST:$PORT"
if [ "$WEB" = true ]; then
    echo "Using web UI"
fi

echo "Executing: $CMD"
eval "$CMD"
