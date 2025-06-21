"""
File size command implementation
"""

import os
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

# Constants
BYTES_PER_KB = 1024.0


class SizeCommand(BaseCommand):
    """Directory size utilities"""

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
        """Show directory sizes"""
        target_dir = args[0] if args else "."

        try:
            target_path = Path(target_dir).resolve()
            if not target_path.exists():
                self.error(f"Path '{target_dir}' does not exist")
                return False

            if target_path.is_file():
                size = self._get_size(target_path)
                Console().print(f"File size: {self._format_size(size)}")
                return True

            self.info(f"Analyzing directory: {target_path}")

            # Get sizes of immediate children
            items = []
            try:
                for item in target_path.iterdir():
                    if item.name.startswith("."):
                        continue  # Skip hidden files/directories
                    size = self._get_size(item)
                    items.append((item.name, size))
            except PermissionError:
                self.error(f"Permission denied accessing '{target_path}'")
                return False

            if items:
                # Sort by size (descending)
                sizes = sorted(items, key=lambda x: x[1], reverse=True)

                table = Table(title=f"Directory sizes in {target_dir}")
                table.add_column("Name", style="cyan")
                table.add_column("Size", style="green")
                table.add_column("Type", style="yellow")

                for name, size in sizes:
                    item_path = target_path / name
                    item_type = "Directory" if item_path.is_dir() else "File"
                    table.add_row(name, self._format_size(size), item_type)

                Console().print(table)
            else:
                self.warning("No items found in directory")

        except Exception as e:
            self.error(str(e))
            return False

        return True


def register_size_command():
    """Register the size command"""
    cmd = SizeCommand()
    registry.register(
        name="size",
        description="Show directory sizes",
        category="file",
        func=cmd.execute,
        usage="file:size [directory_path]",
    )
