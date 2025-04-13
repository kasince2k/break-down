#!/usr/bin/env python3
"""
Setup script for the Obsidian Article Breakdown Agent.

This script helps users set up the agent and its dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if the Python version is compatible."""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        print(f"Current Python version: {sys.version}")
        return False
    return True


def check_poetry_installed():
    """Check if Poetry is installed."""
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Poetry is not installed or not in PATH.")
        print("Please install Poetry: https://python-poetry.org/docs/#installation")
        return False


def check_obsidian_installed():
    """Check if Obsidian is installed."""
    # This is a basic check that looks for common Obsidian installation paths
    # It might not work for all systems or custom installations

    obsidian_paths = []

    if sys.platform == "darwin":  # macOS
        obsidian_paths = [
            "/Applications/Obsidian.app",
            str(Path.home() / "Applications/Obsidian.app"),
        ]
    elif sys.platform == "win32":  # Windows
        obsidian_paths = [
            r"C:\Program Files\Obsidian",
            r"C:\Program Files (x86)\Obsidian",
            str(Path.home() / "AppData/Local/Obsidian"),
        ]
    elif sys.platform.startswith("linux"):  # Linux
        obsidian_paths = [
            "/usr/bin/obsidian",
            "/usr/local/bin/obsidian",
            str(Path.home() / ".local/bin/obsidian"),
        ]

    for path in obsidian_paths:
        if os.path.exists(path):
            return True

    print("Warning: Obsidian installation not found in common locations.")
    print("If Obsidian is installed, please make sure you have an Obsidian vault set up.")
    return True  # Return True anyway, as this is just a warning


def install_dependencies():
    """Install dependencies using Poetry."""
    print("Installing dependencies...")
    try:
        subprocess.run(["poetry", "install"], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def create_env_file():
    """Create a .env file if it doesn't exist."""
    env_example_path = Path("env.example")
    env_path = Path(".env")

    if not env_example_path.exists():
        print("Error: env.example file not found.")
        return False

    if env_path.exists():
        print(".env file already exists. Skipping creation.")
        return True

    try:
        with open(env_example_path, "r") as example_file:
            example_content = example_file.read()

        with open(env_path, "w") as env_file:
            env_file.write(example_content)

        print(".env file created. Please edit it with your API keys and configuration.")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False


def prompt_for_vault_path():
    """Prompt the user for their Obsidian vault path."""
    print(
        "\nTo use the Obsidian Article Breakdown Agent, you need to specify your Obsidian vault path."
    )
    print("This is the folder where your Obsidian notes are stored.")

    default_paths = []
    if sys.platform == "darwin":  # macOS
        default_paths = [str(Path.home() / "Documents/Obsidian")]
    elif sys.platform == "win32":  # Windows
        default_paths = [str(Path.home() / "Documents/Obsidian")]
    elif sys.platform.startswith("linux"):  # Linux
        default_paths = [str(Path.home() / "Obsidian")]

    for path in default_paths:
        if os.path.exists(path) and os.path.isdir(path):
            print(f"\nFound potential Obsidian vault at: {path}")
            break

    print("\nWhen running the agent, you'll need to provide this path:")
    print("python run_agent.py --vault-path /path/to/your/obsidian/vault")

    return True


def main():
    """Main function."""
    print("Setting up the Obsidian Article Breakdown Agent...\n")

    # Check requirements
    if not check_python_version():
        return False

    if not check_poetry_installed():
        return False

    check_obsidian_installed()  # Just a warning, don't fail

    # Install dependencies
    if not install_dependencies():
        return False

    # Create .env file
    if not create_env_file():
        return False

    # Prompt for vault path
    if not prompt_for_vault_path():
        return False

    print("\nSetup complete!")
    print("\nTo run the agent:")
    print("1. Activate the Poetry environment: poetry shell")
    print("2. Run the agent: python run_agent.py --vault-path /path/to/your/obsidian/vault")
    print("\nFor more information, see the README.md file.")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
