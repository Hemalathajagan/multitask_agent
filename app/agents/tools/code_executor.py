import asyncio
import sys


async def execute_python_code(code: str, timeout_seconds: int = 30) -> str:
    """Execute Python code in a sandboxed subprocess and return the output.

    Args:
        code: Python code to execute. Must use print() to produce output.
        timeout_seconds: Maximum execution time in seconds (default 30, max 60).
    """
    timeout_seconds = min(timeout_seconds, 60)

    BLOCKED = [
        "subprocess", "shutil", "rmtree", "system(", "exec(", "eval(",
        "__import__", "importlib", "os.remove", "os.unlink", "os.rmdir"
    ]
    for term in BLOCKED:
        if term in code:
            return f"Error: Use of '{term}' is not permitted for security reasons."

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            process.kill()
            return f"Error: Code execution timed out after {timeout_seconds} seconds."

        output = stdout.decode("utf-8", errors="replace").strip()
        errors = stderr.decode("utf-8", errors="replace").strip()

        result_parts = []
        if output:
            result_parts.append(f"Output:\n{output}")
        if errors:
            result_parts.append(f"Errors:\n{errors}")
        if not result_parts:
            result_parts.append("Code executed successfully (no output).")

        return "\n\n".join(result_parts)
    except Exception as e:
        return f"Failed to execute code: {str(e)}"
