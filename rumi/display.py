"""
Display — RUMI's terminal interface.

Beautiful, colorful console output powered by Rich.
Makes every interaction feel polished and professional.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule


BANNER = """
[bold cyan]
 ██████╗ ██╗   ██╗███╗   ███╗██╗
 ██╔══██╗██║   ██║████╗ ████║██║
 ██████╔╝██║   ██║██╔████╔██║██║
 ██╔══██╗██║   ██║██║╚██╔╝██║██║
 ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝
[/bold cyan]
[dim italic]"What you seek is seeking you." — Rumi[/dim italic]
"""


class Display:
    """Rich terminal UI for RUMI."""

    def __init__(self):
        self.console = Console()

    def welcome(self):
        """Show the startup banner."""
        self.console.print(BANNER, justify="center")
        self.console.print(Rule("[bold blue]Personal AI Assistant[/bold blue]"))
        self.console.print()

    def status(self, message: str):
        """Show a status line during initialization."""
        self.console.print(f"  [dim]▸ {message}[/dim]")

    def ready(self):
        """Announce that RUMI is online."""
        self.console.print()
        self.console.print("[bold green]  ✦ RUMI is online and ready.[/bold green]")
        self.console.print("  [dim]Type your message, or 'exit' to quit.[/dim]")
        self.console.print()

    def prompt(self) -> str:
        """Show the input prompt and wait for the user to type."""
        try:
            return self.console.input("[bold blue]You ➜ [/bold blue]")
        except EOFError:
            return "exit"

    def thinking(self):
        """Show that RUMI is processing."""
        self.console.print("  [dim yellow]⟳ Thinking...[/dim yellow]")

    def tool_call(self, name: str, args: dict):
        """Show which tool RUMI is using (so the user knows what's happening)."""
        args_preview = ", ".join(f"{k}={repr(v)[:60]}" for k, v in args.items())
        self.console.print(
            f"  [dim magenta]⚡ {name}({args_preview})[/dim magenta]"
        )

    def response(self, text: str):
        """Display RUMI's response in a styled panel."""
        self.console.print()
        self.console.print(
            Panel(
                Markdown(text),
                title="[bold cyan]RUMI[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        self.console.print()

    def error(self, message: str):
        """Display an error."""
        self.console.print(f"  [bold red]✗ Error: {message}[/bold red]")

    def goodbye(self):
        """Farewell message."""
        self.console.print()
        self.console.print(
            Panel(
                "[bold cyan]Until next time. — RUMI[/bold cyan]",
                border_style="cyan",
            )
        )

    def confirm(self, action: str) -> bool:
        """Ask the user to confirm a potentially dangerous action."""
        self.console.print(f"\n  [bold yellow]⚠ Confirm:[/bold yellow] {action}")
        answer = self.console.input("  [yellow]Proceed? (y/n): [/yellow]")
        return answer.strip().lower() in ("y", "yes")
