"""
╔══════════════════════════════════════════════════╗
║       RUMI — Your Personal AI Assistant          ║
║       "What you seek is seeking you."            ║
╚══════════════════════════════════════════════════╝

Run this file to start RUMI.

Usage:
    python main.py                → Start normally (text mode)
    python main.py --voice        → Enable voice input/output
    python main.py --model gpt-4  → Use a specific LLM model
    python main.py --provider openai --model gpt-4o  → Use OpenAI
"""

import argparse
import signal
import sys

from rumi.brain import Brain
from rumi.voice import Voice
from rumi.memory import Memory
from rumi.display import Display
import config


def parse_args():
    parser = argparse.ArgumentParser(description="RUMI — Personal AI Assistant")
    parser.add_argument("--voice", action="store_true", help="Enable voice mode")
    parser.add_argument("--model", type=str, help="LLM model name")
    parser.add_argument("--provider", type=str, help="LLM provider (ollama/openai)")
    parser.add_argument("--api-key", type=str, help="API key for the LLM provider")
    parser.add_argument("--base-url", type=str, help="Custom API base URL")
    parser.add_argument("--creator", type=str, help="Your name (how RUMI addresses you)")
    return parser.parse_args()


def main():
    args = parse_args()
    display = Display()

    # ─── Apply CLI overrides ─────────────────────────────────
    if args.model:
        config.LLM_MODEL = args.model
    if args.provider:
        config.LLM_PROVIDER = args.provider
        # Set sensible defaults for known providers
        if args.provider == "openai" and not args.base_url:
            config.LLM_BASE_URL = "https://api.openai.com/v1"
    if args.api_key:
        config.LLM_API_KEY = args.api_key
    if args.base_url:
        config.LLM_BASE_URL = args.base_url
    if args.voice:
        config.VOICE_ENABLED = True
    if args.creator:
        config.CREATOR_NAME = args.creator

    # ─── Show welcome screen ─────────────────────────────────
    display.welcome()

    # ─── Initialize components ───────────────────────────────
    memory = Memory(config.MEMORY_DB)
    voice = Voice(enabled=config.VOICE_ENABLED)
    brain = Brain(memory=memory, display=display)

    display.status(f"Model: {config.LLM_MODEL} via {config.LLM_PROVIDER}")
    display.status(f"Voice: {'ON' if voice.available else 'OFF (text mode)'}")
    display.status(f"Memory: {config.MEMORY_DB}")
    display.ready()

    # ─── Graceful shutdown on Ctrl+C ─────────────────────────
    def shutdown(sig, frame):
        display.goodbye()
        memory.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    # ═══════════════════════════════════════════════════════════
    #  THE MAIN LOOP — Listen → Think → Respond → Repeat
    # ═══════════════════════════════════════════════════════════
    while True:
        try:
            # Get input: from microphone (voice mode) or keyboard (text mode)
            if voice.available:
                user_input = voice.listen()
                if user_input is None:
                    continue  # Didn't catch anything, listen again
            else:
                user_input = display.prompt()

            if not user_input or not user_input.strip():
                continue

            # Exit commands
            if user_input.strip().lower() in ("exit", "quit", "bye", "goodbye"):
                display.goodbye()
                memory.close()
                break

            # Let the Brain handle everything
            response = brain.think(user_input)

            # Speak the response if voice is enabled
            if voice.available:
                voice.speak(response)

        except KeyboardInterrupt:
            display.goodbye()
            memory.close()
            break
        except Exception as e:
            display.error(str(e))


if __name__ == "__main__":
    main()
