"""
╔══════════════════════════════════════════════╗
║         RUMI — Configuration Center          ║
╚══════════════════════════════════════════════╝

All settings for RUMI live here.
Change these values to customize your AI assistant.
Environment variables override defaults (useful for secrets).
"""

import os
from pathlib import Path


# ─── LLM Provider ───────────────────────────────────────────
# Supports: "ollama" (local/free), "openai", or any OpenAI-compatible API
LLM_PROVIDER = os.getenv("RUMI_LLM_PROVIDER", "ollama")
LLM_MODEL    = os.getenv("RUMI_MODEL", "llama3.1")
LLM_BASE_URL = os.getenv("RUMI_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY  = os.getenv("RUMI_API_KEY", "ollama")  # For Ollama, any string works
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS  = 4096
LLM_REQUEST_TIMEOUT = float(os.getenv("RUMI_REQUEST_TIMEOUT", "300"))
LLM_MAX_RETRIES = int(os.getenv("RUMI_MAX_RETRIES", "0"))

# ─── Voice ───────────────────────────────────────────────────
VOICE_ENABLED = os.getenv("RUMI_VOICE", "false").lower() == "true"
WAKE_WORD     = "rumi"
VOICE_RATE    = 175  # Words per minute for TTS

# ─── Memory ─────────────────────────────────────────────────
DATA_DIR  = Path.home() / ".rumi"
MEMORY_DB = DATA_DIR / "memory.db"

# ─── Identity ───────────────────────────────────────────────
CREATOR_NAME = os.getenv("RUMI_CREATOR", "Boss")

# ─── Safety ──────────────────────────────────────────────────
# Shell commands containing these will be blocked with a warning
DANGEROUS_COMMANDS = [
    "rm -rf /", "sudo rm", "mkfs", "dd if=", "> /dev/",
    "shutdown", "reboot", "format c:",
]
CODE_EXECUTION_TIMEOUT = 30  # Max seconds for code/command execution
