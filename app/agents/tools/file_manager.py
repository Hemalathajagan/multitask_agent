from pathlib import Path

WORKSPACE_DIR = Path("workspace")
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html"}


async def create_file(task_id: str, filename: str, content: str) -> str:
    """Create a file in the task's workspace directory.

    Args:
        task_id: The ID of the current task (used for organizing output files).
        filename: Name of the file to create (e.g., report.md, data.csv, config.json).
                  Only .txt, .md, .csv, .json, .html extensions are allowed.
        content: The full content to write to the file.
    """
    try:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return f"Error: Extension '{ext}' not allowed. Use one of: {', '.join(ALLOWED_EXTENSIONS)}"

        safe_filename = Path(filename).name

        task_dir = WORKSPACE_DIR / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)

        file_path = task_dir / safe_filename
        file_path.write_text(content, encoding="utf-8")

        return f"File created successfully: {file_path} ({len(content)} characters)"
    except Exception as e:
        return f"Failed to create file: {str(e)}"
