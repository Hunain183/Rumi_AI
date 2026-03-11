"""
File Tools — Read, write, search, and manage files.

Your filesystem Swiss Army knife.
"""

import os
import glob


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates directories if needed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders in a directory with sizes",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (default: current directory)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": (
                "Search for files by name pattern (glob) or search "
                "inside files for text content"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "Glob pattern (e.g. '*.py') or text to search "
                            "for inside files"
                        ),
                    },
                    "directory": {
                        "type": "string",
                        "description": "Where to search (default: current dir)",
                    },
                    "search_content": {
                        "type": "boolean",
                        "description": "If true, search INSIDE files for the pattern text",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]


def read_file(path: str) -> str:
    """Read and return a file's contents."""
    try:
        with open(path, "r") as f:
            content = f.read()
        if len(content) > 10000:
            content = content[:10000] + f"\n\n[... truncated, total {len(content)} chars ...]"
        return content
    except Exception as e:
        return f"Error reading {path}: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating directories as needed."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Written {len(content)} chars to {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"


def list_directory(path: str = ".") -> str:
    """List directory contents with file sizes."""
    try:
        entries = sorted(os.listdir(path))
        output = []
        for entry in entries:
            full = os.path.join(path, entry)
            if os.path.isdir(full):
                output.append(f"📁 {entry}/")
            else:
                size = os.path.getsize(full)
                output.append(f"📄 {entry}  ({_human_size(size)})")
        return "\n".join(output) or "(empty directory)"
    except Exception as e:
        return f"Error listing {path}: {e}"


def search_files(
    pattern: str, directory: str = ".", search_content: bool = False
) -> str:
    """Search for files by name or by content inside files."""
    try:
        if search_content:
            # Grep-like: search inside files for text
            matches = []
            for root, _, files in os.walk(directory):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if pattern.lower() in line.lower():
                                    matches.append(f"{fpath}:{i}: {line.strip()}")
                                    if len(matches) >= 50:
                                        break
                    except (PermissionError, IsADirectoryError):
                        continue
                    if len(matches) >= 50:
                        break
            return "\n".join(matches) or "No matches found."
        else:
            # Find files by name pattern
            search_glob = os.path.join(directory, "**", pattern)
            files = glob.glob(search_glob, recursive=True)
            return "\n".join(files[:50]) or "No files found."
    except Exception as e:
        return f"Search error: {e}"


def _human_size(size: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
