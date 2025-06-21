"""
Environment commands package
"""

from .path import register_path_command
from .shell import register_shell_command
from .vars import register_vars_command


def register_all_commands():
    """Register all environment commands"""
    register_path_command()
    register_shell_command()
    register_vars_command()
