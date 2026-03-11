"""
Tool Registry — Auto-discovers every skill module in this folder.

Drop a new Python file here and RUMI instantly learns a new skill.
Each tool module should export:
  • DEFINITIONS : list of OpenAI-format tool schemas
  • Functions whose names match the tool names in DEFINITIONS
"""

import importlib
import pkgutil

# Populated automatically by the discovery loop below
TOOL_DEFINITIONS = []   # Sent to the LLM so it knows what tools exist
TOOL_FUNCTIONS   = {}   # Maps tool_name → callable Python function

# Walk every .py file in this package
for _, module_name, _ in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f".{module_name}", __package__)

    # Collect tool definitions
    definitions = getattr(module, "DEFINITIONS", [])
    TOOL_DEFINITIONS.extend(definitions)

    # Map each tool name to its implementation function
    for defn in definitions:
        func_name = defn["function"]["name"]
        func = getattr(module, func_name, None)
        if func:
            TOOL_FUNCTIONS[func_name] = func
