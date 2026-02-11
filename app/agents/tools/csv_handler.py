import csv
import json
from pathlib import Path

WORKSPACE_DIR = Path("workspace")


async def read_csv_file(task_id: str, filename: str) -> str:
    """Read a CSV file from the task workspace and return its contents.

    Args:
        task_id: The task ID whose workspace contains the file.
        filename: Name of the CSV file to read.
    """
    try:
        file_path = WORKSPACE_DIR / f"task_{task_id}" / Path(filename).name
        if not file_path.exists():
            return f"Error: File '{filename}' not found in task {task_id} workspace."

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return "CSV file is empty."

        preview = rows[:20]
        result = f"CSV file: {filename} ({len(rows)} rows, {len(rows[0])} columns)\n"
        result += f"Columns: {', '.join(rows[0].keys())}\n\n"
        result += "First 20 rows:\n"
        result += json.dumps(preview, indent=2)

        if len(rows) > 20:
            result += f"\n\n[{len(rows) - 20} more rows not shown]"

        return result
    except Exception as e:
        return f"Failed to read CSV: {str(e)}"


async def analyze_csv_data(task_id: str, filename: str, operation: str) -> str:
    """Perform basic analysis on a CSV file.

    Args:
        task_id: The task ID whose workspace contains the file.
        filename: Name of the CSV file to analyze.
        operation: Analysis operation - one of: 'summary', 'columns', 'row_count', 'unique_values'.
    """
    try:
        file_path = WORKSPACE_DIR / f"task_{task_id}" / Path(filename).name
        if not file_path.exists():
            return f"Error: File '{filename}' not found in task {task_id} workspace."

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return "CSV file is empty."

        if operation == "summary":
            return (
                f"File: {filename}\n"
                f"Rows: {len(rows)}\n"
                f"Columns ({len(rows[0])}): {', '.join(rows[0].keys())}"
            )
        elif operation == "columns":
            return f"Columns: {', '.join(rows[0].keys())}"
        elif operation == "row_count":
            return f"Row count: {len(rows)}"
        elif operation == "unique_values":
            result = {}
            for col in rows[0].keys():
                vals = set(r[col] for r in rows)
                result[col] = len(vals)
            return f"Unique value counts per column:\n{json.dumps(result, indent=2)}"
        else:
            return f"Unknown operation '{operation}'. Use: summary, columns, row_count, unique_values"
    except Exception as e:
        return f"Failed to analyze CSV: {str(e)}"
