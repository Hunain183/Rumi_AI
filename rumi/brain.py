"""
The Brain — RUMI's reasoning engine.

Connects to an LLM (local via Ollama or cloud via OpenAI) and uses
tool-calling to execute real tasks. The LLM decides which tools to
invoke, the Brain executes them, and loops until the task is done.

This is what makes RUMI autonomous — she doesn't just talk, she ACTS.
"""

import json
import platform
from datetime import datetime

from openai import OpenAI

import config
from rumi.tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
from rumi.memory import Memory
from rumi.display import Display


# ─── RUMI's Personality ─────────────────────────────────────
SYSTEM_PROMPT = """You are RUMI — an elite personal AI assistant with extraordinary intelligence and a calm, sophisticated personality.

Your creator is {creator}. You are their dedicated AI — like Friday is to Tony Stark. Loyal, brilliant, always ready.

== PERSONALITY ==
• Brilliant — solve problems with precision and creativity
• Eloquent — communicate clearly with occasional wit
• Proactive — anticipate needs, suggest improvements
• Honest — never fabricate information; if unsure, say so
• Resourceful — chain multiple tools together for complex tasks

== STYLE ==
• Be concise but thorough — no fluff, no filler
• When executing tasks, briefly state what you're doing
• Show quiet confidence without arrogance
• For complex tasks, break them into steps and execute each one
• Inspired by the poet Rumi — occasionally weave in wisdom when it fits naturally

== CONTEXT ==
Time: {time}
System: {hostname}
Platform: {platform}

== MEMORIES ==
{memories}

== RULES ==
1. ALWAYS use tools when the task requires action — don't just describe, DO IT
2. For destructive operations (delete, format, etc.), warn the user first
3. Chain multiple tools when needed for complex tasks
4. If a tool fails, try an alternative approach
5. Keep responses natural and conversational
"""


class Brain:
    """RUMI's thinking engine — connects understanding to action."""

    def __init__(self, memory: Memory, display: Display):
        self.memory = memory
        self.display = display
        self.conversation = []   # This session's chat messages
        self.max_history = 50    # Keep last N messages for context window

        # Connect to the LLM (works with Ollama, OpenAI, or any compatible API)
        self.client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
        )
        self.model = config.LLM_MODEL

        # Give the memory tools access to our Memory instance
        from rumi.tools import memory_ops
        memory_ops.set_memory(memory)

    def think(self, user_message: str) -> str:
        """
        Process a user message through the full pipeline:
        understand → plan → execute tools → respond.
        """
        # Save the user's message
        self.memory.save("user", user_message)
        self.conversation.append({"role": "user", "content": user_message})
        self._trim_history()

        # Build the full prompt (system + history)
        messages = self._build_messages()

        self.display.thinking()

        # ═══ The Autonomous Tool-Calling Loop ═══
        # The LLM can call tools, see results, call more tools, etc.
        # This continues until the LLM gives a final text response.
        max_rounds = 15  # Safety limit against infinite loops

        for _ in range(max_rounds):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_DEFINITIONS or None,
                    temperature=config.LLM_TEMPERATURE,
                    max_tokens=config.LLM_MAX_TOKENS,
                )
            except Exception as e:
                # If tool-calling fails (unsupported model), retry without tools
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=config.LLM_TEMPERATURE,
                        max_tokens=config.LLM_MAX_TOKENS,
                    )
                except Exception as e2:
                    return f"I couldn't reach the LLM. Check your config. Error: {e2}"

            choice = response.choices[0]
            message = choice.message

            # ── If the LLM wants to call tools, execute them ──
            if message.tool_calls:
                messages.append(message)

                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    self.display.tool_call(name, args)
                    result = self._execute_tool(name, args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })

                continue  # Go back to the LLM with the tool results

            # ── No tool calls = final response ──
            final = message.content or "Done."
            break
        else:
            final = "I reached my execution limit. Let me know if you'd like me to continue."

        # Save and display
        self.memory.save("assistant", final)
        self.conversation.append({"role": "assistant", "content": final})
        self.display.response(final)

        return final

    def _build_messages(self) -> list:
        """Assemble system prompt + conversation history for the LLM."""
        facts = self.memory.get_facts()
        memory_text = (
            "\n".join(f"• {k}: {v}" for k, v in facts.items())
            if facts else "No stored memories yet."
        )

        system = SYSTEM_PROMPT.format(
            creator=config.CREATOR_NAME,
            time=datetime.now().strftime("%A, %B %d, %Y at %I:%M %p"),
            hostname=platform.node(),
            platform=f"{platform.system()} {platform.release()}",
            memories=memory_text,
        )

        return [{"role": "system", "content": system}] + list(self.conversation)

    def _execute_tool(self, name: str, args: dict) -> str:
        """Look up a tool by name and run it."""
        if name not in TOOL_FUNCTIONS:
            return f"Unknown tool: '{name}'"

        try:
            result = TOOL_FUNCTIONS[name](**args)
            return str(result) if result is not None else "Done."
        except Exception as e:
            return f"Tool error ({name}): {e}"

    def _trim_history(self):
        """Keep conversation within the context window limit."""
        if len(self.conversation) > self.max_history:
            self.conversation = self.conversation[-self.max_history:]
