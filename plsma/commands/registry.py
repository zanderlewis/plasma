"""
Command registry system for Plasma
"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class CommandInfo:
    """Information about a registered command"""

    name: str
    description: str
    category: str
    func: Callable
    usage: str = ""


class CommandRegistry:
    """Central registry for all Plasma commands"""

    def __init__(self):
        self._commands: dict[str, CommandInfo] = {}

    def register(
        self,
        name: str,
        description: str,
        category: str,
        func: Callable,
        usage: str = "",
    ):
        """Register a new command"""
        command_key = f"{category}:{name}"
        self._commands[command_key] = CommandInfo(
            name=name,
            description=description,
            category=category,
            func=func,
            usage=usage,
        )

    def get_command(self, command_key: str) -> CommandInfo | None:
        """Get command info by key (category:name)"""
        return self._commands.get(command_key)

    def get_all_commands(self) -> dict[str, CommandInfo]:
        """Get all registered commands"""
        return self._commands.copy()

    def get_commands_by_category(self, category: str) -> dict[str, CommandInfo]:
        """Get all commands in a specific category"""
        return {
            key: cmd for key, cmd in self._commands.items() if cmd.category == category
        }

    def get_categories(self) -> list[str]:
        """Get all available categories"""
        categories = set()
        for cmd in self._commands.values():
            categories.add(cmd.category)
        return sorted(categories)


# Global registry instance
registry = CommandRegistry()
