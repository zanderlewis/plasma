"""
PATH management command implementation
"""

import os
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

console = Console()


class PathCommand(BaseCommand):
    """PATH environment variable management utilities"""

    def execute(self, args):
        """Manage PATH environment variable"""
        if not args:
            self._show_path()
            return True

        action = args[0].lower()

        if action == "show":
            self._show_path()
        elif action == "add" and len(args) > 1:
            self._add_to_path(args[1])
        elif action == "remove" and len(args) > 1:
            self._remove_from_path(args[1])
        elif action == "clean":
            self._clean_path()
        else:
            self._show_automatic_help()

        return True

    def _show_automatic_help(self):
        """Show automatic help for path command"""
        actions = [
            {"name": "show", "description": "Show current PATH entries"},
            {"name": "add", "args": "<path>", "description": "Add directory to PATH"},
            {"name": "remove", "args": "<path>", "description": "Remove directory from PATH"},
            {"name": "clean", "description": "Analyze PATH for issues"},
        ]
        self.show_automatic_help(
            "env:path [show|add|remove|clean] [path]",
            actions,
            "Manage PATH environment variable"
        )

    def _show_path(self):
        """Display current PATH entries"""
        self.info("Current PATH entries:")

        path_entries = os.environ.get("PATH", "").split(os.pathsep)

        table = Table(title="PATH Entries")
        table.add_column("Index", style="cyan", no_wrap=True)
        table.add_column("Path", style="white")
        table.add_column("Exists", style="green")

        for i, entry in enumerate(path_entries, 1):
            if entry:  # Skip empty entries
                exists = "✓" if Path(entry).exists() else "✗"
                exists_style = "green" if Path(entry).exists() else "red"
                table.add_row(
                    str(i), entry, f"[{exists_style}]{exists}[/{exists_style}]"
                )

        console.print(table)

    def _add_to_path(self, new_path):
        """Add a directory to PATH in shell config"""
        path_obj = Path(new_path).expanduser().resolve()

        if not path_obj.exists():
            if not self.ask_confirmation(
                f"Path '{path_obj}' does not exist. Add anyway?"
            ):
                return

        if not path_obj.is_dir() and path_obj.exists():
            self.error(f"'{path_obj}' is not a directory")
            return

        # Detect shell and get config file
        shell_config = self._get_shell_config_file()
        if not shell_config:
            self.error("Could not determine shell configuration file")
            return

        # Check if path is already in config
        try:
            with open(shell_config) as f:
                content = f.read()
                if str(path_obj) in content:
                    self.warning(f"Path '{path_obj}' may already be in {shell_config}")
                    if not self.ask_confirmation("Add anyway?"):
                        return
        except FileNotFoundError:
            # Config file doesn't exist, we'll create it
            pass

        # Add PATH export line
        export_line = f'\nexport PATH="{path_obj}:$PATH"'

        try:
            with open(shell_config, "a") as f:
                f.write(export_line)

            self.success(f"Added '{path_obj}' to PATH in {shell_config}")
            self.info(
                f"Restart your shell or run 'source {shell_config}' to apply changes"
            )

        except Exception as e:
            self.error(f"Failed to update {shell_config}: {e}")

    def _remove_from_path(self, remove_path):
        """Remove a directory from PATH in shell config"""
        path_obj = Path(remove_path).expanduser().resolve()

        shell_config = self._get_shell_config_file()
        if not shell_config:
            self.error("Could not determine shell configuration file")
            return

        try:
            with open(shell_config) as f:
                lines = f.readlines()

            # Filter out lines that add this path to PATH
            new_lines = []
            removed_count = 0

            for line in lines:
                if (
                    f'export PATH="{path_obj}:$PATH"' in line
                    or f"export PATH='{path_obj}:$PATH'" in line
                    or f'PATH="{path_obj}:$PATH"' in line
                    or f"PATH='{path_obj}:$PATH'" in line
                ):
                    removed_count += 1
                    continue
                new_lines.append(line)

            if removed_count > 0:
                with open(shell_config, "w") as f:
                    f.writelines(new_lines)

                self.success(
                    f"Removed {removed_count} PATH entries for '{path_obj}' from {shell_config}"
                )
                self.info("Restart your shell to apply changes")
            else:
                self.warning(
                    f"No PATH entries found for '{path_obj}' in {shell_config}"
                )

        except FileNotFoundError:
            self.error(f"Configuration file {shell_config} not found")
        except Exception as e:
            self.error(f"Failed to update {shell_config}: {e}")

    def _clean_path(self):
        """Show duplicate and non-existent PATH entries"""
        self.info("Analyzing PATH for issues...")

        path_entries = os.environ.get("PATH", "").split(os.pathsep)
        seen = set()
        duplicates = []
        non_existent = []

        for entry in path_entries:
            if entry:
                if entry in seen:
                    duplicates.append(entry)
                else:
                    seen.add(entry)

                if not Path(entry).exists():
                    non_existent.append(entry)

        if duplicates:
            console.print("\n[yellow]Duplicate PATH entries:[/yellow]")
            for dup in duplicates:
                console.print(f"  • {dup}")

        if non_existent:
            console.print("\n[red]Non-existent PATH entries:[/red]")
            for missing in non_existent:
                console.print(f"  • {missing}")

        if not duplicates and not non_existent:
            self.success(
                "PATH looks clean - no duplicates or non-existent entries found"
            )

    def _get_shell_config_file(self):
        """Determine the appropriate shell configuration file"""
        shell = os.environ.get("SHELL", "").split("/")[-1]
        home = Path.home()

        # Shell-specific config files
        config_files = {
            "zsh": [".zshrc", ".zprofile"],
            "bash": [".bashrc", ".bash_profile"],
            "fish": [".config/fish/config.fish"],
        }

        if shell in config_files:
            for config in config_files[shell]:
                config_path = home / config
                if config_path.exists():
                    return str(config_path)
            # Return the primary config file even if it doesn't exist
            return str(home / config_files[shell][0])

        # Default fallback
        return str(home / ".profile")


def register_path_command():
    """Register the path command"""
    cmd = PathCommand()
    registry.register(
        name="path",
        description="Manage PATH environment variable",
        category="env",
        func=cmd.execute,
        usage="env:path [show|add|remove|clean] [path]",
    )
