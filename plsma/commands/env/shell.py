"""
Shell configuration management command implementation
"""

import os
import shutil
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax

from ..base import BaseCommand
from ..registry import registry

console = Console()


class ShellCommand(BaseCommand):
    """Shell configuration file management utilities"""

    def execute(self, args):
        """Manage shell configuration files"""
        if not args:
            self._show_config_info()
            return True

        action = args[0].lower()

        if action == "info":
            self._show_config_info()
        elif action == "edit":
            self._edit_config()
        elif action == "backup":
            self._backup_config()
        elif action == "reload":
            self._reload_config()
        elif action == "add" and len(args) > 1:
            self._add_line(" ".join(args[1:]))
        else:
            self._show_automatic_help()

        return True

    def _show_automatic_help(self):
        """Show automatic help for shell command"""
        actions = [
            {"name": "info", "description": "Show shell config info"},
            {"name": "edit", "description": "Edit config in default editor"},
            {"name": "backup", "description": "Create backup of config"},
            {"name": "reload", "description": "Reload shell configuration"},
            {"name": "add", "args": "<text>", "description": "Add line to config file"},
        ]
        self.show_automatic_help(
            "env:shell [info|edit|backup|reload|add] [text]",
            actions,
            "Manage shell configuration files"
        )

    def _show_config_info(self):
        """Show information about shell configuration"""
        shell = os.environ.get("SHELL", "").split("/")[-1]
        config_file = self._get_shell_config_file()

        self.info(f"Current shell: {shell}")
        self.info(f"Configuration file: {config_file}")

        if Path(config_file).exists():
            stat = Path(config_file).stat()
            size = stat.st_size
            self.info(f"File size: {size} bytes")

            # Show last few lines
            try:
                with open(config_file) as f:
                    lines = f.readlines()
                    if lines:
                        console.print(
                            f"\n[bold]Last 5 lines of {Path(config_file).name}:[/bold]"
                        )
                        last_lines = lines[-5:]
                        syntax = Syntax(
                            "".join(last_lines),
                            "bash",
                            theme="monokai",
                            line_numbers=True,
                        )
                        console.print(syntax)
            except Exception as e:
                self.warning(f"Could not read config file: {e}")
        else:
            self.warning("Configuration file does not exist")

    def _edit_config(self):
        """Open shell config in default editor"""
        config_file = self._get_shell_config_file()
        editor = os.environ.get("EDITOR", "nano")

        self.info(f"Opening {config_file} in {editor}")
        result = self._run_command(f"{editor} {config_file}", capture_output=False)

        if result.returncode == 0:
            self.success("Configuration file edited successfully")
            self.info("Run 'plasma env:shell reload' to apply changes")
        else:
            self.error("Failed to open editor")

    def _backup_config(self):
        """Create a backup of the shell configuration"""
        config_file = self._get_shell_config_file()

        if not Path(config_file).exists():
            self.error("Configuration file does not exist")
            return

        backup_file = f"{config_file}.backup"
        try:
            shutil.copy2(config_file, backup_file)
            self.success(f"Backup created: {backup_file}")
        except Exception as e:
            self.error(f"Failed to create backup: {e}")

    def _reload_config(self):
        """Reload shell configuration"""
        config_file = self._get_shell_config_file()

        if not Path(config_file).exists():
            self.error("Configuration file does not exist")
            return

        self.info(f"Reloading {config_file}")
        result = self._run_command(f"source {config_file}")

        if result.returncode == 0:
            self.success("Configuration reloaded successfully")
        else:
            self.warning("Could not reload configuration in current shell")
            self.info(
                "You may need to restart your shell or run the source command manually"
            )

    def _add_line(self, line):
        """Add a line to the shell configuration"""
        config_file = self._get_shell_config_file()

        # Ensure the line starts with a newline if file exists and doesn't end with newline
        try:
            if Path(config_file).exists():
                with open(config_file) as f:
                    content = f.read()
                    if content and not content.endswith("\n"):
                        line = "\n" + line
            else:
                # Create parent directories if they don't exist
                Path(config_file).parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "a") as f:
                f.write(line + "\n")

            self.success(f"Added line to {config_file}: {line}")
            self.info("Run 'plasma env:shell reload' to apply changes")

        except Exception as e:
            self.error(f"Failed to add line to config: {e}")

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


def register_shell_command():
    """Register the shell command"""
    cmd = ShellCommand()
    registry.register(
        name="shell",
        description="Manage shell configuration files",
        category="env",
        func=cmd.execute,
        usage="env:shell [info|edit|backup|reload|add] [text]",
    )
