<div align="center">

```
 ██████╗ ██╗   ██╗███╗   ███╗██╗
 ██╔══██╗██║   ██║████╗ ████║██║
 ██████╔╝██║   ██║██╔████╔██║██║
 ██╔══██╗██║   ██║██║╚██╔╝██║██║
 ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝
```

**Your Personal AI Assistant — Like Friday, But Yours.**

*"What you seek is seeking you." — Rumi*

</div>

---

## What is RUMI?

RUMI is a **fully autonomous AI assistant** that doesn't just talk — she **acts**. Give her a task, and she uses real tools to get it done: running commands, searching the web, writing code, managing files, monitoring your system, and remembering everything across sessions.

Think **Friday from Iron Man** — a loyal, intelligent AI that's always ready, runs locally, and is entirely under your control.

## Architecture

```
main.py              ← Start here. The main loop: listen → think → act → respond.
gui.py               ← Desktop GUI. Chat + system monitor + memory viewer.
config.py            ← All settings (LLM, voice, safety) in one place.

rumi/
├── brain.py         ← The AI core: LLM + autonomous tool-calling loop
├── memory.py        ← SQLite persistent memory (conversations + facts)
├── display.py       ← Beautiful Rich terminal UI
├── voice.py         ← Speech recognition + text-to-speech (optional)
├── gui/             ← Desktop GUI components (PyQt6)
│   ├── main_window.py ← Main application window
│   ├── widgets.py     ← Chat bubbles, system monitor, memory viewer
│   ├── worker.py      ← Background thread for the brain
│   └── styles.py      ← Dark theme + cyan accents
└── tools/           ← Drop-in skill modules (auto-discovered!)
    ├── __init__.py   ← Auto-registers every tool in this folder
    ├── system.py     ← Shell commands, open apps, system info
    ├── web.py        ← Web search (DuckDuckGo), fetch pages
    ├── code.py       ← Run Python code, create scripts
    ├── files.py      ← Read/write/search files
    ├── math_ops.py   ← Calculations, unit conversions
    ├── reminder.py   ← Set timed reminders
    ├── monitor.py    ← CPU, RAM, disk, processes
    ├── memory_ops.py ← Remember/recall facts about you
    └── datetime_ops.py ← Date/time queries and calculations
```

## How It Works

1. **You speak or type** a request
2. **The Brain** sends your message + all available tool definitions to the LLM
3. **The LLM decides** which tools to call (can chain multiple tools autonomously)
4. **Tools execute** — real shell commands, real file I/O, real web searches
5. **Results flow back** to the LLM, which can call more tools or give a final answer
6. **RUMI responds** with text (and voice, if enabled)

The key innovation is the **autonomous tool-calling loop** — RUMI can chain up to 15 tool calls in a single request, solving complex multi-step problems without human intervention.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up an LLM

**Option A: Local with Ollama (free, private)**
```bash
# Install Ollama: https://ollama.com
ollama pull llama3.1
python main.py
```

**Option B: OpenAI API**
```bash
export RUMI_API_KEY="sk-your-key-here"
python main.py --provider openai --model gpt-4o
```

**Option C: Any OpenAI-Compatible API**
```bash
python main.py --base-url http://your-api:8000/v1 --model your-model
```

### 3. Start RUMI

#### Terminal Mode
```bash
# Text mode (default)
python main.py

# With voice
python main.py --voice

# Custom settings
python main.py --model llama3.1 --creator "Tony"
```

#### Desktop GUI
```bash
python gui.py
```

The GUI features:
- **Chat Interface** — Beautiful message bubbles on the left
- **System Monitor** — Real-time CPU, RAM, disk, and temperature (right panel)
- **Memory Viewer** — Stored facts and conversation history
- **Dark Theme** — Cyan accents matching RUMI's aesthetic
- **Non-blocking** — Brain runs on background threads, UI stays responsive

## What RUMI Can Do

| Skill | Examples |
|-------|----------|
| **System Control** | "Open Firefox", "What's my IP address?", "List running processes" |
| **Code Execution** | "Write a Python script that sorts my photos by date", "Run this code..." |
| **Web Search** | "Search for the latest Python release", "What's the weather in NYC?" |
| **File Management** | "Find all PDF files in Downloads", "Read config.py", "Create a new file" |
| **Math & Units** | "What's 15% of 3400?", "Convert 72°F to Celsius" |
| **System Monitor** | "How much RAM am I using?", "Find the biggest files on my disk" |
| **Memory** | "Remember that my server IP is 192.168.1.100", "What do you know about me?" |
| **Reminders** | "Remind me to check the build in 30 minutes" |
| **Date/Time** | "What day of the week is Dec 25, 2025?", "How many days until New Year?" |
| **Multi-Step Tasks** | "Check my disk usage, find the 5 biggest files, and suggest what to delete" |

## Adding New Skills

RUMI auto-discovers tools. Just drop a new `.py` file in `rumi/tools/`:

```python
# rumi/tools/my_skill.py
"""My custom skill description."""

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "What this tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {"type": "string", "description": "First argument"}
                },
                "required": ["arg1"],
            },
        },
    },
]

def my_tool(arg1: str) -> str:
    """Implementation."""
    return f"Result for {arg1}"
```

Restart RUMI and she instantly knows the new skill. No configuration needed.

## Desktop GUI

RUMI includes a modern PyQt6-based desktop application with:

### Features
- **Chat Interface** — Beautiful message bubbles with cyan accents
- **System Monitor** — Real-time stats (CPU, RAM, disk, temperature)
- **Memory Viewer** — See all stored facts and conversation history
- **Dark Theme** — Elegant dark mode matching RUMI's aesthetic
- **Non-blocking UI** — Brain runs on background threads, keeping the app responsive
- **One-click Launch** — Just run `python gui.py`

### GUI Architecture
The GUI separates concerns cleanly:
- `main_window.py` — Main application window, event handling
- `widgets.py` — Reusable UI components (chat bubbles, monitors, tables)
- `worker.py` — Background thread runner for the brain (keeps UI responsive)
- `styles.py` — Centralized dark theme + colors

Message flow:
1. User types → `ChatWindow.send_message` signal
2. Main window catches signal → creates `BrainWorker` thread
3. Worker runs `brain.think()` in background
4. When done → emits `response_received` signal
5. Main window updates UI (adds message to chat, refreshes memory viewer)

All without blocking the UI!

## Configuration

All settings live in `config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RUMI_LLM_PROVIDER` | `ollama` | LLM provider |
| `RUMI_MODEL` | `llama3.1` | Model name |
| `RUMI_BASE_URL` | `http://localhost:11434/v1` | API endpoint |
| `RUMI_API_KEY` | `ollama` | API key |
| `RUMI_VOICE` | `false` | Enable voice mode |
| `RUMI_CREATOR` | `Boss` | How RUMI addresses you |

## Voice Setup (Optional)

Voice requires additional system packages:

```bash
# Ubuntu/Debian
sudo apt install portaudio19-dev espeak

# macOS
brew install portaudio

# Then install Python voice packages
pip install SpeechRecognition pyttsx3 PyAudio
```

## License

MIT — Use it, modify it, make it yours.