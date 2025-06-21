"""
Server commands package
"""

from .find import register_find_command
from .kill import register_kill_command
from .ports import register_ports_command


def register_all_commands():
    """Register all server commands"""
    register_kill_command()
    register_find_command()
    register_ports_command()
