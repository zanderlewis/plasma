"""
File commands package
"""

from .backup import register_backup_command
from .size import register_size_command


def register_all_commands():
    """Register all file commands"""
    register_size_command()
    register_backup_command()
