"""
System Tools — Control the operating system.

Open applications, run shell commands, get system info.
This is what lets RUMI actually DO things on your machine.
"""

import subprocess
import platform

import config


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": (
                "Execute a shell command and return its output. "
                "Use for: listing files, git operations, installing packages, "
                "checking status, and anything you'd type in a terminal."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open an application, file, or URL with the system default handler",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "App name, file path, or URL to open",
                    }
                },
                "required": ["target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get detailed info about the OS, hardware, and environment",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def run_shell_command(command: str) -> str:
    """Execute a shell command safely and return its output."""
    # Block dangerous commands
    for pattern in config.DANGEROUS_COMMANDS:
        if pattern.lower() in command.lower():
            return (
                f"⚠ BLOCKED: Command contains '{pattern.strip()}' which is "
                f"potentially destructive. Command: {command}"
            )

    try:
        result = subprocess.run(
            command,
            shell=True,  # Needed for pipes, redirects, etc.
            capture_output=True,
            text=True,
            timeout=config.CODE_EXECUTION_TIMEOUT,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        return output.strip() or "(command completed, no output)"

    except subprocess.TimeoutExpired:
        return f"Command timed out after {config.CODE_EXECUTION_TIMEOUT}s"
    except Exception as e:
        return f"Command failed: {e}"


def open_application(target: str) -> str:
    """Open an application, file, or URL using the OS default handler."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", target])
        elif system == "Windows":
            subprocess.Popen(["start", "", target], shell=True)
        else:
            subprocess.Popen(["xdg-open", target])
        return f"Opened: {target}"
    except Exception as e:
        return f"Failed to open {target}: {e}"


def get_system_info() -> str:
    """Gather comprehensive system information."""
    import psutil

    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Hostname": platform.node(),
        "Architecture": platform.machine(),
        "Python": platform.python_version(),
        "CPU Cores": psutil.cpu_count(),
        "RAM Total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
        "RAM Used": f"{psutil.virtual_memory().percent}%",
        "Disk Total": f"{psutil.disk_usage('/').total / (1024**3):.1f} GB",
        "Disk Used": f"{psutil.disk_usage('/').percent}%",
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())
