"""
Git commands package
"""

from .status import register_status_command
from .sync import register_sync_command
from .undo import register_undo_command


def register_all_commands():
    """Register all git commands"""
    register_status_command()
    register_sync_command()
    register_undo_command()
