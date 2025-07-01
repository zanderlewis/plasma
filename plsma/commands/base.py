"""
Base command class for Plasma commands
"""

import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Tool configuration
TOOL_COMMAND = "plasma"


class BaseCommand:
    """Base class for all Plasma commands"""

    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.category: str = "general"
        self.usage: str = ""
        self.tool_command = TOOL_COMMAND

    def _run_command(self, cmd, capture_output=True):
        """Run a shell command and return the result"""
        result = subprocess.run(
            cmd, check=False, shell=True, capture_output=capture_output, text=True
        )
        return result

    def print_help(self):
        """Print help information for this command"""
        console.print(f"[bold]{self.name}[/bold] - {self.description}")
        if self.usage:
            console.print(f"Usage: {self.tool_command} {self.usage}")

    def error(self, message: str):
        """Print an error message"""
        console.print(f"[red][ERROR][/red] {message}")

    def success(self, message: str):
        """Print a success message"""
        console.print(f"[green][SUCCESS][/green] {message}")

    def info(self, message: str):
        """Print an info message"""
        console.print(f"[blue][INFO][/blue] {message}")

    def warning(self, message: str):
        """Print a warning message"""
        console.print(f"[yellow][WARNING][/yellow] {message}")

    def show_automatic_help(
        self, command_usage: str, actions: list[dict], description: str = ""
    ):
        """Show automatic help based on command actions"""
        # Create help content
        title = Text(f"Help: {command_usage.split()[0]}", style="bold blue")

        content = Text()
        if description:
            content.append("Description: ", style="bold")
            content.append(f"{description}\n\n", style="white")

        content.append("Usage: ", style="bold")
        content.append(f"{self.tool_command} {command_usage}\n\n", style="cyan")

        if actions:
            content.append("Available Actions:\n", style="bold")
            for action in actions:
                action_name = action.get("name", "")
                action_desc = action.get("description", "")
                action_args = action.get("args", "")

                if action_args:
                    content.append(f"  {action_name} {action_args}", style="cyan")
                else:
                    content.append(f"  {action_name}", style="cyan")

                if action_desc:
                    content.append(f" - {action_desc}\n", style="white")
                else:
                    content.append("\n", style="white")

        console.print(Panel(content, title=title, style="blue", padding=(1, 2)))

    def ask_confirmation(self, message: str) -> bool:
        """Ask for user confirmation"""
        return console.input(f"{message} (y/n): ").lower().startswith("y")
