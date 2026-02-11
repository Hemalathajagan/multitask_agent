import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
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


async def edit_csv_file(file_path: str, updates_json: str) -> str:
    """Edit specific cells in a CSV file on the local filesystem.

    Args:
        file_path: Full path to the CSV file (e.g., C:/Users/user/Documents/data.csv).
        updates_json: JSON string of row/column updates, e.g. '{"0": {"Name": "John", "Age": "30"}, "2": {"Name": "Jane"}}'.
                      Keys are row indices (0-based, excluding header), values are column:value dicts.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."

        if path.suffix.lower() != '.csv':
            return f"Error: File must be a CSV file. Got: {path.suffix}"

        updates = json.loads(updates_json)
        if not isinstance(updates, dict):
            return "Error: updates_json must be a JSON object with row indices as keys."

        # Read existing CSV
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        if not fieldnames:
            return "Error: CSV file has no headers."

        changes = []
        for row_idx_str, col_updates in updates.items():
            row_idx = int(row_idx_str)
            if row_idx < 0 or row_idx >= len(rows):
                changes.append(f"  Row {row_idx}: SKIPPED (out of range, max={len(rows)-1})")
                continue
            for col_name, new_value in col_updates.items():
                if col_name not in fieldnames:
                    changes.append(f"  Row {row_idx}, '{col_name}': SKIPPED (column not found)")
                    continue
                old_value = rows[row_idx].get(col_name, "")
                rows[row_idx][col_name] = str(new_value)
                changes.append(f"  Row {row_idx}, '{col_name}': '{old_value}' → '{new_value}'")

        # Write back
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        result = f"Successfully updated CSV '{file_path}':\n"
        result += "\n".join(changes)
        logger.info(f"CSV edit: {file_path}, {len(changes)} changes")
        return result

    except json.JSONDecodeError:
        return "Error: Invalid JSON in updates_json."
    except Exception as e:
        return f"Failed to edit CSV file: {str(e)}"
