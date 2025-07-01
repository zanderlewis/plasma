"""
Help command implementation
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .base import BaseCommand
from .registry import registry

console = Console()


class HelpCommand(BaseCommand):
    """Stylistic help command for Plasma"""

    def __init__(self):
        super().__init__()
        self.name = "help"
        self.description = "Display help information about commands"
        self.category = "general"
        self.usage = "help [command]"

    def execute(self, args):
        """Display help information"""
        if args and len(args) > 0:
            # Show help for specific command
            command_name = args[0]
            return self._show_command_help(command_name)
        else:
            # Show general help
            return self._show_general_help()

    def _show_general_help(self):
        """Display general help with all commands"""
        # Create header
        title = Text("Plasma Help", style="bold blue")
        subtitle = Text("A powerful development toolkit", style="italic")

        header_content = Text()
        header_content.append(title)
        header_content.append("\n")
        header_content.append(subtitle)
        header_content.append("\n\n")
        header_content.append("Usage: ", style="bold")
        header_content.append(f"{self.tool_command} <command> [args...]", style="cyan")

        console.print(Panel(header_content, style="blue", padding=(1, 2)))

        # Add footer with additional help info
        footer_content = Text()
        footer_content.append("Examples:\n", style="bold")
        footer_content.append(f"  {self.tool_command} list", style="cyan")
        footer_content.append("               Show all commands\n")
        footer_content.append(f"  {self.tool_command} list:git", style="cyan")
        footer_content.append("           Show git commands\n")
        footer_content.append(f"  {self.tool_command} help <command>", style="cyan")
        footer_content.append("     Show help for specific command\n")
        footer_content.append(f"  {self.tool_command} --version", style="cyan")
        footer_content.append("          Show version information")

        console.print(
            Panel(footer_content, title="Quick Start", style="green", padding=(1, 2))
        )

        return True

    def _show_command_help(self, command_name):
        """Display help for a specific command"""
        command_info = registry.get_command(command_name)

        if not command_info:
            self.error(f"Command '{command_name}' not found")
            console.print(
                f"[yellow]Run '{self.tool_command} help' to see available commands[/yellow]"
            )
            return False

        # Create detailed command info
        title = Text(f"Help: {command_name}", style="bold blue")

        content = Text()
        content.append("Description: ", style="bold")
        content.append(f"{command_info.description}\n", style="white")

        content.append("Category: ", style="bold")
        content.append(f"{command_info.category}\n", style="magenta")

        if hasattr(command_info, "usage") and command_info.usage:
            content.append("Usage: ", style="bold")
            content.append(f"{self.tool_command} {command_info.usage}\n", style="cyan")

        console.print(Panel(content, title=title, style="blue", padding=(1, 2)))

        # Show related commands in the same category
        related_commands = registry.get_commands_by_category(command_info.category)
        if len(related_commands) > 1:  # More than just this command
            table = Table(
                title=f"Related {command_info.category.title()} Commands",
                show_header=True,
            )
            table.add_column("Command", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")

            for cmd_name, cmd_info in sorted(related_commands.items()):
                if cmd_name != command_name:  # Don't show the current command
                    table.add_row(cmd_name, cmd_info.description)

            console.print(table)

        return True


def register_help_command():
    """Register the help command"""
    cmd = HelpCommand()
    registry.register(
        name="help",  # Register as just "help", not "general:help"
        description="Display stylistic help information about commands",
        category="general",
        func=cmd.execute,
        usage="help [command]",
    )
