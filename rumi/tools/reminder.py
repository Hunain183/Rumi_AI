"""
Reminder Tools — Set and manage timed reminders.

Reminders run on a background thread and print a notification
to the terminal when they trigger.
"""

import threading
import time
from datetime import datetime, timedelta


# Active reminders (in-memory for this session)
_reminders = []
_checker_thread = None


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": (
                "Set a reminder that triggers after a delay. "
                "Examples: 'in 5 minutes', 'in 1 hour', 'in 30 seconds'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "What to remind about",
                    },
                    "delay_minutes": {
                        "type": "number",
                        "description": "Minutes from now to trigger",
                    },
                },
                "required": ["message", "delay_minutes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "Show all active (pending) reminders",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def set_reminder(message: str, delay_minutes: float) -> str:
    """Set a reminder that fires after delay_minutes."""
    trigger_time = datetime.now() + timedelta(minutes=delay_minutes)

    _reminders.append({
        "message": message,
        "trigger": trigger_time.isoformat(),
        "set_at": datetime.now().isoformat(),
    })

    _start_checker()

    return (
        f"✓ Reminder set: '{message}' — triggers at "
        f"{trigger_time.strftime('%I:%M %p')}"
    )


def list_reminders() -> str:
    """Show all pending reminders."""
    if not _reminders:
        return "No active reminders."

    now = datetime.now()
    lines = []
    for i, r in enumerate(_reminders, 1):
        trigger = datetime.fromisoformat(r["trigger"])
        remaining = trigger - now
        if remaining.total_seconds() > 0:
            mins = int(remaining.total_seconds() / 60)
            lines.append(
                f"{i}. {r['message']} — in {mins} min "
                f"({trigger.strftime('%I:%M %p')})"
            )
        else:
            lines.append(f"{i}. {r['message']} — TRIGGERED")

    return "\n".join(lines)


def _start_checker():
    """Ensure the background reminder checker is running."""
    global _checker_thread
    if _checker_thread and _checker_thread.is_alive():
        return
    _checker_thread = threading.Thread(target=_check_loop, daemon=True)
    _checker_thread.start()


def _check_loop():
    """Background loop: checks every 15s and prints due reminders."""
    while True:
        now = datetime.now()
        due = [
            r for r in _reminders
            if datetime.fromisoformat(r["trigger"]) <= now
        ]
        for r in due:
            print(f"\n  🔔 REMINDER: {r['message']}")
            _reminders.remove(r)

        if not _reminders:
            break  # No more reminders — thread exits

        time.sleep(15)
