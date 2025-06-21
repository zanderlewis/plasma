"""
Environment variables management command implementation
"""

import os
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

console = Console()

# Constants
MIN_ARGS_FOR_SET = 2
MIN_ARGS_FOR_EXPORT = 2
MAX_VALUE_DISPLAY_LENGTH = 100


class VarsCommand(BaseCommand):
    """Environment variables management utilities"""

    def execute(self, args):
        """Manage environment variables"""
        if not args:
            self._show_env_vars()
            return True

        action = args[0].lower()

        if action == "show":
            filter_pattern = args[1] if len(args) > 1 else None
            self._show_env_vars(filter_pattern)
        elif action == "get" and len(args) > 1:
            self._get_env_var(args[1])
        elif action == "set" and len(args) > MIN_ARGS_FOR_SET:
            self._set_env_var(args[1], " ".join(args[2:]))
        elif action == "unset" and len(args) > 1:
            self._unset_env_var(args[1])
        elif action == "export" and len(args) > MIN_ARGS_FOR_EXPORT:
            self._export_env_var(args[1], " ".join(args[2:]))
        elif action == "clear":
            self._clear_custom_vars()
        else:
            self._show_automatic_help()

        return True

    def _show_automatic_help(self):
        """Show automatic help for vars command"""
        actions = [
            {"name": "show", "args": "[filter]", "description": "Show environment variables"},
            {"name": "get", "args": "<name>", "description": "Get specific variable"},
            {"name": "set", "args": "<name> <value>", "description": "Set variable (session only)"},
            {"name": "unset", "args": "<name>", "description": "Unset variable (session only)"},
            {"name": "export", "args": "<name> <value>", "description": "Export to shell config"},
            {"name": "clear", "description": "Remove custom exports from config"},
        ]
        self.show_automatic_help(
            "env:vars [show|get|set|unset|export|clear] [name] [value]",
            actions,
            "Manage environment variables"
        )

    def _show_env_vars(self, filter_pattern=None):
        """Display environment variables"""
        env_vars = dict(os.environ)

        if filter_pattern:
            env_vars = {
                k: v for k, v in env_vars.items() if filter_pattern.lower() in k.lower()
            }

        table = Table(
            title=f"Environment Variables{f' (filtered by: {filter_pattern})' if filter_pattern else ''}"
        )
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Value", style="white", max_width=80)

        for key in sorted(env_vars.keys()):
            value = env_vars[key]
            # Truncate very long values
            if len(value) > MAX_VALUE_DISPLAY_LENGTH:
                value = value[:97] + "..."
            table.add_row(key, value)

        console.print(table)
        console.print(f"\n[dim]Total: {len(env_vars)} variables[/dim]")

    def _get_env_var(self, var_name):
        """Get a specific environment variable"""
        value = os.environ.get(var_name)
        if value is not None:
            console.print(f"[cyan]{var_name}[/cyan] = [white]{value}[/white]")
        else:
            self.warning(f"Environment variable '{var_name}' is not set")

    def _set_env_var(self, var_name, value):
        """Set an environment variable for current session"""
        os.environ[var_name] = value
        self.success(f"Set {var_name} = {value}")
        self.warning("This change is only for the current session")
        self.info(f"To make it permanent, use: plasma env:vars export {var_name} {value}")

    def _unset_env_var(self, var_name):
        """Unset an environment variable"""
        if var_name in os.environ:
            del os.environ[var_name]
            self.success(f"Unset environment variable '{var_name}'")
            self.warning("This change is only for the current session")
        else:
            self.warning(f"Environment variable '{var_name}' is not set")

    def _export_env_var(self, var_name, value):
        """Export an environment variable to shell config"""
        shell_config = self._get_shell_config_file()
        if not shell_config:
            self.error("Could not determine shell configuration file")
            return

        # Check if variable is already exported
        try:
            with open(shell_config) as f:
                content = f.read()
                if f"export {var_name}=" in content:
                    self.warning(
                        f"Variable '{var_name}' may already be exported in {shell_config}"
                    )
                    if not self.ask_confirmation("Add anyway?"):
                        return
        except FileNotFoundError:
            # Config file doesn't exist, we'll create it
            pass

        # Add export line
        export_line = f'\nexport {var_name}="{value}"'

        try:
            with open(shell_config, "a") as f:
                f.write(export_line)

            self.success(f"Exported {var_name} to {shell_config}")
            self.info(
                f"Restart your shell or run 'source {Path(shell_config).name}' to apply changes"
            )

            # Also set for current session
            os.environ[var_name] = value
            self.info("Variable also set for current session")

        except Exception as e:
            self.error(f"Failed to update {shell_config}: {e}")

    def _clear_custom_vars(self):
        """Clear custom environment variables from shell config"""
        shell_config = self._get_shell_config_file()
        if not shell_config:
            self.error("Could not determine shell configuration file")
            return

        self.warning(
            "This will remove all 'export VAR=value' lines from your shell config"
        )
        if not self.ask_confirmation("Are you sure you want to continue?"):
            return

        try:
            with open(shell_config) as f:
                lines = f.readlines()

            # Filter out export lines (be conservative)
            new_lines = []
            removed_count = 0

            for line in lines:
                stripped = line.strip()
                if (
                    stripped.startswith("export ")
                    and "=" in stripped
                    and not any(
                        sys_var in stripped
                        for sys_var in ["PATH", "SHELL", "HOME", "USER"]
                    )
                ):
                    removed_count += 1
                    continue
                new_lines.append(line)

            if removed_count > 0:
                # Create backup first
                backup_file = f"{shell_config}.backup"
                with open(backup_file, "w") as f:
                    f.writelines(lines)

                with open(shell_config, "w") as f:
                    f.writelines(new_lines)

                self.success(
                    f"Removed {removed_count} export statements from {shell_config}"
                )
                self.info(f"Backup created: {backup_file}")
                self.info("Restart your shell to apply changes")
            else:
                self.info("No custom export statements found to remove")

        except FileNotFoundError:
            self.error(f"Configuration file {shell_config} not found")
        except Exception as e:
            self.error(f"Failed to update {shell_config}: {e}")

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


def register_vars_command():
    """Register the vars command"""
    cmd = VarsCommand()
    registry.register(
        name="vars",
        description="Manage environment variables",
        category="env",
        func=cmd.execute,
        usage="env:vars [show|get|set|unset|export|clear] [name] [value]",
    )
