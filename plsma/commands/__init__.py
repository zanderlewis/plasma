"""
Commands package for Plasma

This package contains all the command modules organized by category.
Each category has its own subdirectory with individual command files.
"""

from plsma.commands import env, file, git, help, ip, project, server


def register_all_commands():
    """Register all commands from all modules"""
    help.register_help_command()
    file.register_all_commands()
    git.register_all_commands()
    server.register_all_commands()
    ip.register_all_commands()
    project.register_all_commands()
    env.register_all_commands()


__all__ = [
    "register_all_commands",
]
