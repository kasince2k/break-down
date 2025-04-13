# Explanation

1. **Configuration:** Set `VAULT_PATH` to the correct location of your Obsidian vault. `STATE_DIR` defines where the script stores its state (last run time, processed files).
2. **State Management:**
    * `_load_last_run_time`/`_save_last_run_time`: Read/write the timestamp of the last successful run from/to `last_run.txt`. Uses UTC and ISO format for consistency. Returns epoch (0) if the file doesn't exist on the first run.
    * `_load_processed_files`/`_save_processed_files`: Read/write the set of *absolute paths* (as strings) of already processed files from/to `processed_files.json`. Using a set allows for efficient checking (`in`). Absolute paths prevent issues if the script is run from different directories.
3. **`primary_analyst(filepath: Path)`:** This is a **placeholder**. You **must** replace its contents with your actual Python code that needs to run on each new file. It receives the `pathlib.Path` object of the new file.
4. **`find_new_markdown_files()`:**
    * Loads the `last_run_time` and the `processed_files` set.
    * Records the `current_run_time` (this will be saved at the end for the *next* run).
    * Uses `VAULT_PATH.glob('**/*.md')` to find all markdown files recursively.
    * For each file:
        * Gets its modification time (`st_mtime`) and converts it to a timezone-aware `datetime` object (UTC).
        * Gets the file's resolved absolute path as a string.
        * Checks if `mod_time > last_run_time` **AND** if `abs_path_str not in processed_files`.
        * If both conditions are true, it calls `primary_analyst` with the file's `Path` object.
        * If `primary_analyst` completes without error, the file's absolute path string is added to the `processed_files` set.
    * After checking all files, if any new files were processed, it saves the updated `processed_files` set.
    * Finally, it saves the `current_run_time` to `last_run.txt` to be used as the `last_run_time` in the next execution.
5. **`if __name__ == "__main__":`:** Ensures the monitoring logic runs when the script is executed directly.

**How to Use:**

1. **Save:** Save the code as `utils/obsidian_monitor.py` (or any name you prefer).
2. **Configure:** **Crucially, change `/path/to/your/obsidian/vault`** in the `VAULT_PATH` constant to the actual path of your vault.
3. **Implement:** Replace the placeholder `primary_analyst` function with your analysis logic.
4. **Run:** Execute the script periodically (e.g., using `cron` on Linux/macOS or Task Scheduler on Windows).

    * Example Cron Job (runs every hour):

        ```bash
        0 * * * * /usr/bin/python3 /path/to/your/script/utils/obsidian_monitor.py >> /path/to/your/logfile.log 2>&1
        ```

        *(Adjust paths to your Python interpreter and script location)*
