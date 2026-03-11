"""
Date & Time Tools — Current time, date math, day-of-week lookups.
"""

import time as time_module
from datetime import datetime, timedelta


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date, time, day of week, and timezone",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "date_calculation",
            "description": (
                "Calculate days between dates, add/subtract days, "
                "or find the day of week for any date"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["days_between", "add_days", "day_of_week"],
                        "description": "The calculation to perform",
                    },
                    "date1": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format",
                    },
                    "date2": {
                        "type": "string",
                        "description": "Second date for days_between (YYYY-MM-DD)",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Days to add/subtract (for add_days)",
                    },
                },
                "required": ["operation", "date1"],
            },
        },
    },
]


def get_current_datetime() -> str:
    """Get comprehensive date/time information."""
    now = datetime.now()
    return (
        f"Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Time: {now.strftime('%I:%M:%S %p')}\n"
        f"Timezone: {time_module.tzname[0]}\n"
        f"Week: {now.isocalendar()[1]} of {now.year}\n"
        f"Day of year: {now.timetuple().tm_yday}/365"
    )


def date_calculation(
    operation: str,
    date1: str,
    date2: str = None,
    days: int = None,
) -> str:
    """Perform date calculations."""
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")

        if operation == "days_between" and date2:
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            diff = abs((d2 - d1).days)
            return f"{diff} days between {date1} and {date2}"

        elif operation == "add_days" and days is not None:
            result = d1 + timedelta(days=days)
            return f"{date1} + {days} days = {result.strftime('%Y-%m-%d (%A)')}"

        elif operation == "day_of_week":
            return f"{date1} is a {d1.strftime('%A')}"

        else:
            return "Invalid operation or missing parameters."

    except ValueError as e:
        return f"Date error: {e}. Use YYYY-MM-DD format."
