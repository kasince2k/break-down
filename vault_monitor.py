import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

# --- Configuration ---
VAULT_PATH = Path(
    "/Users/roshanmurthy/Desktop/testvault/test1/test1"
)  # ! CHANGE THIS !
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
        with open(PROCESSED_FILES_FILE, "r") as f:
            # Store absolute paths as strings for consistency
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def _save_processed_files(processed_files: Set[str]):
    """Saves the set of processed file paths to the state file."""
    with open(PROCESSED_FILES_FILE, "w") as f:
        # Convert Path objects or ensure strings before saving
        json.dump(list(processed_files), f)


# --- Core Monitoring Logic ---


def find_new_markdown_files_and_analyze():
    """
    Finds new markdown files in the vault since the last run
    and triggers the primary_analyst function for each.
    """
    if not VAULT_PATH.is_dir():
        print(f"Error: Vault path not found or not a directory: {VAULT_PATH}")
        return

    last_run_time = _load_last_run_time()
    processed_files = _load_processed_files()
    current_run_time = datetime.now(timezone.utc)  # Use timezone-aware datetime
    new_files_found = False

    print(f"Checking for files modified since: {last_run_time}")

    # Iterate through all markdown files recursively
    for md_file in VAULT_PATH.glob("**/*.md"):
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
                    processed_files.add(abs_path_str)  # Add after successful analysis
                    new_files_found = True
                except Exception as e:
                    print(f"Error processing file {md_file}: {e}")
                    # Decide if you want to add it to processed_files even on error
                    # processed_files.add(abs_path_str) # Optional: uncomment to avoid retrying failed files
            else:
                print(f"{md_file} already analyzed!")

        except OSError as e:
            print(f"Error accessing file {md_file}: {e}")
            continue  # Skip to next file if stat fails

    if new_files_found:
        print("Saving updated processed files list.")
        _save_processed_files(processed_files)
    else:
        print("No new markdown files found to process.")

    # Always save the current run time for the next execution
    _save_last_run_time(current_run_time)
    print(
        f"Finished check. Next check will look for files modified after: {current_run_time}"
    )


if __name__ == "__main__":
    find_new_markdown_files_and_analyze()
