"""
Memory Tools — Remember and recall information.

RUMI's way of storing facts, preferences, and notes
that persist across sessions. The user can say things like
"remember that my favorite language is Python" and RUMI stores it.
"""

# The Memory instance is injected by the Brain at startup
_memory = None


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": (
                "Store a fact or preference to remember across sessions. "
                "Use when the user shares personal info, preferences, or "
                "asks you to remember something."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Short label (e.g. 'user_name', 'fav_language')",
                    },
                    "value": {
                        "type": "string",
                        "description": "The information to remember",
                    },
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_fact",
            "description": "Retrieve a previously stored fact or preference",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The label of the fact to recall",
                    }
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search through past conversations for a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_facts",
            "description": "List everything RUMI remembers about the user",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def set_memory(memory_instance):
    """Called by Brain.__init__ to inject the Memory instance."""
    global _memory
    _memory = memory_instance


def remember_fact(key: str, value: str) -> str:
    """Store a persistent fact."""
    if not _memory:
        return "Memory system not initialized."
    _memory.save_fact(key, value)
    return f"✓ Remembered: {key} = {value}"


def recall_fact(key: str) -> str:
    """Retrieve a stored fact."""
    if not _memory:
        return "Memory system not initialized."
    value = _memory.get_fact(key)
    return value if value else f"Nothing stored for '{key}'"


def search_memory(query: str) -> str:
    """Search past conversations by keyword."""
    if not _memory:
        return "Memory system not initialized."
    results = _memory.search(query)
    if not results:
        return f"No past conversations match '{query}'"
    lines = []
    for r in results:
        lines.append(f"[{r['time']}] {r['role']}: {r['content'][:200]}")
    return "\n".join(lines)


def list_all_facts() -> str:
    """Show everything RUMI has remembered."""
    if not _memory:
        return "Memory system not initialized."
    facts = _memory.get_facts()
    if not facts:
        return "No facts stored yet. Tell me things to remember!"
    return "\n".join(f"• {k}: {v}" for k, v in facts.items())
