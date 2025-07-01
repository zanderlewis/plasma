"""
File backup command implementation
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from rich.console import Console

from ..base import BaseCommand
from ..registry import registry

BYTES_PER_KB = 1024.0


class BackupCommand(BaseCommand):
    """Directory backup utilities"""

    def _get_size(self, path):
        """Get size of file or directory in bytes"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
            return total
        return 0

    def _format_size(self, size_bytes):
        """Format size in human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
            if size_bytes < BYTES_PER_KB:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= BYTES_PER_KB
        return f"{size_bytes:.2f} YB"

    def execute(self, args):
        """Create backup of directory"""
        if not args:
            self.error("Directory path required")
            self._show_automatic_help()
            return False

        source_dir = args[0]
        backup_name = args[1] if len(args) > 1 else None

        source_path = Path(source_dir).resolve()
        if not source_path.exists():
            self.error(f"Directory '{source_dir}' does not exist")
            return False

        if not source_path.is_dir():
            self.error(f"'{source_dir}' is not a directory")
            return False

        try:
            # Generate backup name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_name:
                backup_dir_name = f"{backup_name}_{timestamp}"
            else:
                backup_dir_name = f"{source_path.name}_backup_{timestamp}"

            backup_path = source_path.parent / backup_dir_name

            self.info(f"Creating backup: {backup_path}")

            # Create backup
            shutil.copytree(source_path, backup_path)

            backup_size = self._get_size(backup_path)
            self.success("Backup created successfully")
            Console().print(f"Location: {backup_path}")
            Console().print(f"Size: {self._format_size(backup_size)}")

        except Exception as e:
            self.error(f"Creating backup: {e}")
            return False

        return True

    def _show_automatic_help(self):
        """Show automatic help for backup command"""
        actions = [
            {"name": "<source_directory>", "description": "Directory to backup"},
            {
                "name": "<source_directory> <backup_name>",
                "description": "Directory to backup with custom name",
            },
        ]
        self.show_automatic_help(
            "file:backup <source_directory> [backup_name]",
            actions,
            "Create a timestamped backup of a directory",
        )


def register_backup_command():
    """Register the backup command"""
    cmd = BackupCommand()
    registry.register(
        name="backup",
        description="Create backup of directory",
        category="file",
        func=cmd.execute,
        usage="file:backup <source_directory> [backup_name]",
    )
