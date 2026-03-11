"""
System Monitor — Track CPU, RAM, disk, battery, and processes.

Uses psutil to give RUMI real-time awareness of the machine's health.
"""

import os
import psutil


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "system_status",
            "description": (
                "Get current system resource usage: CPU, RAM, disk, "
                "network, battery, and optionally top processes"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "include_processes": {
                        "type": "boolean",
                        "description": "Include top processes by memory (default: false)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_large_files",
            "description": "Find the largest files in a directory tree",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to scan (default: home)",
                    },
                    "count": {
                        "type": "integer",
                        "description": "How many files to return (default: 10)",
                    },
                },
                "required": [],
            },
        },
    },
]


def system_status(include_processes: bool = False) -> str:
    """Get a comprehensive snapshot of system resource usage."""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    report = [
        f"🖥  CPU:     {cpu}% used ({psutil.cpu_count()} cores)",
        f"🧠 RAM:     {mem.percent}% used "
        f"({mem.used / (1024**3):.1f} / {mem.total / (1024**3):.1f} GB)",
        f"💾 Disk:    {disk.percent}% used "
        f"({disk.used / (1024**3):.1f} / {disk.total / (1024**3):.1f} GB)",
    ]

    # Battery (laptops only)
    battery = psutil.sensors_battery()
    if battery:
        plug = "plugged in" if battery.power_plugged else "on battery"
        report.append(f"🔋 Battery: {battery.percent}% — {plug}")

    # Network totals
    net = psutil.net_io_counters()
    report.append(
        f"🌐 Network: ↑ {net.bytes_sent / (1024**2):.1f} MB sent, "
        f"↓ {net.bytes_recv / (1024**2):.1f} MB received"
    )

    # Top processes by memory
    if include_processes:
        report.append("\n📊 Top 10 Processes (by RAM):")
        procs = []
        for proc in psutil.process_iter(
            ["pid", "name", "memory_percent", "cpu_percent"]
        ):
            try:
                procs.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        procs.sort(
            key=lambda p: p.get("memory_percent", 0) or 0, reverse=True
        )
        for p in procs[:10]:
            report.append(
                f"  • {p['name']} (PID {p['pid']}) — "
                f"RAM: {p.get('memory_percent', 0):.1f}%, "
                f"CPU: {p.get('cpu_percent', 0):.1f}%"
            )

    return "\n".join(report)


def find_large_files(directory: str = None, count: int = 10) -> str:
    """Scan a directory tree and return the largest files."""
    if directory is None:
        directory = os.path.expanduser("~")

    files = []
    try:
        for root, _, filenames in os.walk(directory):
            for fname in filenames:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    files.append((fpath, size))
                except (OSError, PermissionError):
                    continue
            if len(files) > 100_000:  # Safety limit
                break
    except PermissionError:
        return f"Permission denied: {directory}"

    files.sort(key=lambda x: x[1], reverse=True)

    lines = [f"Top {count} largest files in {directory}:\n"]
    for path, size in files[:count]:
        lines.append(f"  {_human_size(size):>10}  {path}")

    return "\n".join(lines) if files else "No files found."


def _human_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
