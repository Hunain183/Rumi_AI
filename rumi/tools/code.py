"""
Code Tools — Write and execute code.

Runs Python code in an isolated subprocess with a timeout.
Can also create script files on disk.
"""

import subprocess
import tempfile
import os

import config


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": (
                "Execute Python code and return the output. Use for calculations, "
                "data processing, automation scripts, and any Python task."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute",
                    }
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_script",
            "description": "Save code to a file on disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Where to save the script",
                    },
                    "code": {
                        "type": "string",
                        "description": "The code to write",
                    },
                },
                "required": ["file_path", "code"],
            },
        },
    },
]


def run_python_code(code: str) -> str:
    """Execute Python code in a separate process and capture output."""
    # Write to a temp file so the subprocess can run it
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=config.CODE_EXECUTION_TIMEOUT,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        return output.strip() or "(code ran successfully, no output)"

    except subprocess.TimeoutExpired:
        return f"Timed out after {config.CODE_EXECUTION_TIMEOUT}s"
    except Exception as e:
        return f"Execution error: {e}"
    finally:
        os.unlink(temp_path)  # Clean up temp file


def create_script(file_path: str, code: str) -> str:
    """Write code to a file on disk."""
    try:
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w") as f:
            f.write(code)
        return f"Script saved to {file_path}"
    except Exception as e:
        return f"Failed to save: {e}"
