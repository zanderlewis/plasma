"""
Project commands package
"""

from .license import register_license_command


def register_all_commands():
    """Register all project commands"""
    register_license_command()
