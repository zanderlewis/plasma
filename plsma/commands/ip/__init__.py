"""
IP commands package
"""

from .list import register_list_command
from .ping import register_ping_command
from .port import register_port_command
from .subnet import register_subnet_command
from .validate import register_validate_command


def register_all_commands():
    """Register all IP commands"""
    register_list_command()
    register_validate_command()
    register_subnet_command()
    register_ping_command()
    register_port_command()
