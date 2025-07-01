"""
Plasma CLI - Main entry point for the development toolkit
"""

import sys

import click
from rich.console import Console
from rich.table import Table

from plsma.commands import register_all_commands
from plsma.commands.registry import registry
from plsma.utils import get_version

console = Console()

# Configuration constants for dynamic usage
TOOL_NAME = "plasma"
TOOL_COMMAND = "plasma"
TOOL_VERSION = get_version()


class PlasmaCLI:
    """Main CLI class that handles command registration and execution"""

    def __init__(self):
        self._register_commands()

    def _register_commands(self):
        """Register all commands from modules"""
        # Register commands from all modules
        register_all_commands()

    def list_commands(self):
        """Display all available commands grouped by category"""
        table = Table(title=f"Available {TOOL_NAME} Commands")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        table.add_column("Category", style="green")

        commands = registry.get_all_commands()
        for cmd_name, cmd_info in sorted(commands.items()):
            table.add_row(cmd_name, cmd_info.description, cmd_info.category)

        console.print(table)

    def execute_command(self, command_name: str, args: list):
        """Execute a specific command"""
        # Handle dynamic list commands
        if command_name.startswith("list:"):
            category = command_name.split(":", 1)[1]
            return self.list_commands_by_category(category)

        command_info = registry.get_command(command_name)

        # If command not found, try to find it without category prefix
        if not command_info:
            # Special handling for common commands like 'help'
            for category in self.get_categories():
                potential_key = f"{category}:{command_name}"
                command_info = registry.get_command(potential_key)
                if command_info:
                    break

        if not command_info:
            console.print(f"[red]Error: Command '{command_name}' not found[/red]")
            console.print(
                f"[yellow]Run '{TOOL_COMMAND} list' to see available commands[/yellow]"
            )

            # Suggest list:category commands if available
            categories = self.get_categories()
            if categories:
                categories_str = ", ".join(categories)
                console.print(f"[blue]Or try: {TOOL_COMMAND} list:<category>[/blue]")
                console.print(f"[blue]Available categories: {categories_str}[/blue]")
            return False

        try:
            return command_info.func(args)
        except Exception as e:
            console.print(f"[red]Error executing command '{command_name}': {e}[/red]")
            return False

    def get_categories(self):
        """Get all available command categories"""
        return registry.get_categories()

    def list_commands_by_category(self, category: str):
        """Display commands for a specific category"""
        category_commands = registry.get_commands_by_category(category)

        if not category_commands:
            console.print(
                f"[yellow]No commands found in category '{category}'[/yellow]"
            )
            available_categories = self.get_categories()
            console.print(
                f"[blue]Available categories: {', '.join(available_categories)}[/blue]"
            )
            return False

        table = Table(title=f"{category.title()} Commands")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        for cmd_name, cmd_info in sorted(category_commands.items()):
            table.add_row(cmd_name, cmd_info.description)

        console.print(table)
        return True


@click.command()
@click.argument("command", required=False)
@click.argument("args", nargs=-1)
@click.option("--version", "-v", is_flag=True, help="Show version information")
def main(command: str | None, args: tuple, version: bool):
    if version:
        console.print(f"{TOOL_NAME} version {TOOL_VERSION}")
        return

    cli = PlasmaCLI()

    if not command or command == "list":
        cli.list_commands()
        return

    if command == "help":
        success = cli.execute_command("help", list(args))
        if not success:
            sys.exit(1)
        return

    # Execute the command
    success = cli.execute_command(command, list(args))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
