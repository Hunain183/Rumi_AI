"""
Math Tools — Calculations and unit conversions.

Evaluates math expressions safely (no arbitrary code execution)
and converts between common units.
"""

import math


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Evaluate a math expression. Supports: +, -, *, /, **, "
                "sqrt, sin, cos, tan, log, log2, pi, e, factorial, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression (e.g. 'sqrt(144) + 2**10')",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_units",
            "description": (
                "Convert between units: temperature, distance, weight, "
                "data sizes, time, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "The value to convert"},
                    "from_unit": {
                        "type": "string",
                        "description": "Source unit (e.g. 'celsius', 'km', 'pounds', 'GB')",
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "Target unit (e.g. 'fahrenheit', 'miles', 'kg', 'MB')",
                    },
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    },
]


# Safe namespace for eval — only math functions, NO builtins
_SAFE_MATH = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
_SAFE_MATH.update({"abs": abs, "round": round, "min": min, "max": max})


def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        # __builtins__ = {} prevents access to import, exec, eval, etc.
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return str(result)
    except Exception as e:
        return f"Math error: {e}"


# ─── Unit Conversion ─────────────────────────────────────────

# Conversion factors to a common base unit per category
_LENGTH = {  # base: meters
    "mm": 0.001, "cm": 0.01, "m": 1, "meter": 1, "meters": 1, "km": 1000,
    "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
    "ft": 0.3048, "feet": 0.3048, "foot": 0.3048,
    "yard": 0.9144, "yards": 0.9144, "yd": 0.9144,
    "mile": 1609.34, "miles": 1609.34, "mi": 1609.34,
}

_WEIGHT = {  # base: grams
    "mg": 0.001, "g": 1, "gram": 1, "grams": 1,
    "kg": 1000, "kilogram": 1000,
    "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495,
    "lb": 453.592, "lbs": 453.592, "pound": 453.592, "pounds": 453.592,
    "ton": 907185, "tons": 907185,
}

_DATA = {  # base: bytes
    "b": 1, "byte": 1, "bytes": 1,
    "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4, "pb": 1024**5,
}

_TIME = {  # base: seconds
    "ms": 0.001, "millisecond": 0.001,
    "s": 1, "sec": 1, "second": 1, "seconds": 1,
    "min": 60, "minute": 60, "minutes": 60,
    "hr": 3600, "hour": 3600, "hours": 3600,
    "day": 86400, "days": 86400,
    "week": 604800, "weeks": 604800,
    "month": 2592000, "months": 2592000,
    "year": 31536000, "years": 31536000,
}

_ALL_TABLES = [_LENGTH, _WEIGHT, _DATA, _TIME]


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units."""
    f, t = from_unit.lower().strip(), to_unit.lower().strip()

    # Temperature is special (not a simple ratio)
    temp_names = {"celsius", "fahrenheit", "kelvin", "c", "f", "k"}
    if f in temp_names and t in temp_names:
        return _convert_temperature(value, f, t)

    # Try each conversion table
    for table in _ALL_TABLES:
        if f in table and t in table:
            result = value * table[f] / table[t]
            return f"{value} {from_unit} = {result:.6g} {to_unit}"

    return f"Unknown conversion: {from_unit} → {to_unit}"


def _convert_temperature(value: float, f: str, t: str) -> str:
    """Handle temperature conversions."""
    # Normalize short names
    f = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}.get(f, f)
    t = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}.get(t, t)

    # Convert to Celsius first
    if f == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif f == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value

    # Then from Celsius to target
    if t == "fahrenheit":
        result = celsius * 9 / 5 + 32
    elif t == "kelvin":
        result = celsius + 273.15
    else:
        result = celsius

    return f"{value}° {f.title()} = {result:.2f}° {t.title()}"
