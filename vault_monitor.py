import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Set, Optional
import time
import logging
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from python_connector.obsidian_chat import run_breakdown_for_file

# --- Load .env file ---
load_dotenv()
# ----------------------

# Configure logging (adjust level and format as needed)
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# --- Configuration ---
VAULT_PATH = Path("/Users/ashwin/personal/Obsidian/Sample/Extra/Extra/Extra/Test/Test Vault")  # Vault Path
STATE_DIR = Path.home() / ".obsidian_monitor_state"
LAST_RUN_FILE = STATE_DIR / "last_run.txt"
PROCESSED_FILES_FILE = STATE_DIR / "processed_files.json"
# --- End Configuration ---

# Ensure state directory exists
STATE_DIR.mkdir(parents=True, exist_ok=True)

# --- Placeholder for the analysis function ---
def primary_analyst(filepath: Path):
    """
    Placeholder function to be called for each new markdown file.
    Replace this with your actual analysis logic.
    """
    print(f"Analyzing new file: {filepath}")
    # Example: Read content, process, etc.
    # content = filepath.read_text()
    # ... your analysis code ...

# --- Persistence Helper Functions ---

def _load_last_run_time() -> datetime:
    """Loads the last run timestamp from the state file."""
    try:
        timestamp_str = LAST_RUN_FILE.read_text()
        # Assume ISO format with timezone from previous runs
        return datetime.fromisoformat(timestamp_str)
    except (FileNotFoundError, ValueError):
        # Return epoch if file doesn't exist or content is invalid
        return datetime.fromtimestamp(0, tz=timezone.utc)

def _save_last_run_time(run_time: datetime):
    """Saves the current run timestamp to the state file."""
    # Store in ISO format with UTC timezone for consistency
    LAST_RUN_FILE.write_text(run_time.astimezone(timezone.utc).isoformat())

def _load_processed_files() -> Set[str]:
    """Loads the set of processed file paths from the state file."""
    try:
        with open(PROCESSED_FILES_FILE, 'r') as f:
            # Store absolute paths as strings for consistency
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def _save_processed_files(processed_files: Set[str]):
    """Saves the set of processed file paths to the state file."""
    with open(PROCESSED_FILES_FILE, 'w') as f:
        # Convert Path objects or ensure strings before saving
        json.dump(list(processed_files), f)

# --- Core Monitoring Logic ---

def find_new_markdown_files():
    """
    Finds new markdown files in the vault since the last run
    and triggers the primary_analyst function for each.
    """
    if not VAULT_PATH.is_dir():
        print(f"Error: Vault path not found or not a directory: {VAULT_PATH}")
        return

    last_run_time = _load_last_run_time()
    processed_files = _load_processed_files()
    current_run_time = datetime.now(timezone.utc) # Use timezone-aware datetime
    new_files_found = False

    print(f"Checking for files modified since: {last_run_time}")

    # Iterate through all markdown files recursively
    for md_file in VAULT_PATH.glob('**/*.md'):
        if not md_file.is_file():
            continue

        try:
            # Get modification time (timezone-aware)
            mtime_timestamp = md_file.stat().st_mtime
            mod_time = datetime.fromtimestamp(mtime_timestamp, tz=timezone.utc)

            # Use resolved absolute path string for reliable tracking
            abs_path_str = str(md_file.resolve())

            # Condition 1: File modified since last run
            # Condition 2: File not already processed
            if mod_time > last_run_time and abs_path_str not in processed_files:
                try:
                    primary_analyst(md_file)
                    processed_files.add(abs_path_str) # Add after successful analysis
                    new_files_found = True
                except Exception as e:
                    print(f"Error processing file {md_file}: {e}")
                    # Decide if you want to add it to processed_files even on error
                    # processed_files.add(abs_path_str) # Optional: uncomment to avoid retrying failed files

        except OSError as e:
            print(f"Error accessing file {md_file}: {e}")
            continue # Skip to next file if stat fails

    if new_files_found:
        print("Saving updated processed files list.")
        _save_processed_files(processed_files)
    else:
        print("No new markdown files found to process.")

    # Always save the current run time for the next execution
    _save_last_run_time(current_run_time)
    print(f"Finished check. Next check will look for files modified after: {current_run_time}")

# --- New file handling logic ---

# Make sure this points to the directory *containing* your Clippings folder
# VAULT_BASE_PATH should be the path configured in .env for ObsidianChat
VAULT_BASE_PATH = os.getenv("VAULT_PATH") # Read from .env ideally, or hardcode carefully
CLIPPINGS_DIR_NAME = "Clippings" # Name of the folder to monitor within the vault

if not VAULT_BASE_PATH:
    logging.error("VAULT_PATH environment variable not set. Cannot determine monitoring path.")
    exit(1)

watch_path = Path(VAULT_BASE_PATH) / CLIPPINGS_DIR_NAME

if not watch_path.is_dir():
    logging.error(f"Clippings directory not found at expected path: {watch_path}")
    exit(1)

class NewFileHandler(FileSystemEventHandler):
    """Handles file system events."""
    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory and event.src_path.endswith(".md"):
            src_path = Path(event.src_path)
            # Check if the event is directly within the monitored Clippings folder
            if src_path.parent == watch_path:
                filename_without_ext = src_path.stem
                logging.info(f"Detected new article in {CLIPPINGS_DIR_NAME}: {filename_without_ext}.md")

                # Run the asynchronous breakdown process synchronously in a new event loop
                try:
                    # Use asyncio.run() to execute the async function from this sync thread
                    asyncio.run(self.run_breakdown_async(filename_without_ext))
                    # Logging moved to run_breakdown_async upon completion/failure
                except Exception as e:
                    # Catch potential errors from asyncio.run() itself or re-raised exceptions
                    logging.error(f"Error running breakdown process for {filename_without_ext}: {e}")
            else:
                 logging.debug(f"Ignoring file created in sub-directory: {event.src_path}")
        else:
            logging.debug(f"Ignoring event (not .md file or is directory): {event.src_path}")

    async def run_breakdown_async(self, filename_without_ext: str):
        """Wrapper to run the breakdown and log errors."""
        try:
            await run_breakdown_for_file(filename_without_ext)
            logging.info(f"Breakdown task completed for: {filename_without_ext}")
        except Exception as e:
            logging.error(f"Breakdown task failed for '{filename_without_ext}': {e}", exc_info=True)

if __name__ == "__main__":
    logging.info(f"Starting Obsidian Vault Monitor for directory: {watch_path}")
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False) # Monitor only Clippings folder, not subdirs
    observer.start()
    logging.info("Monitor started. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping monitor...")
        observer.stop()
    except Exception as e:
        logging.error(f"An unexpected error occurred in the monitor: {e}", exc_info=True)
        observer.stop()
        
    observer.join()
    logging.info("Monitor stopped.")