"""
IP port command implementation
"""

import socket

from ..base import BaseCommand
from ..registry import registry

# Constants
MIN_PORT = 1
MAX_PORT = 65535


class PortCommand(BaseCommand):
    """Port checking utilities"""

    def execute(self, args):
        """Check if a port is open on localhost"""
        if not args:
            self.error("Port number required")
            self._show_automatic_help()
            return False

        # Validate and parse arguments
        port, host = self._parse_port_args(args)
        if port is None:
            return False

        # Check port connection
        return self._check_port_connection(port, host)

    def _parse_port_args(self, args):
        """Parse port check arguments and validate"""
        try:
            port = int(args[0])
            host = args[1] if len(args) > 1 else "localhost"
        except ValueError:
            self.error("Invalid port number")
            return None, None

        if not (MIN_PORT <= port <= MAX_PORT):
            self.error(f"Port must be between {MIN_PORT} and {MAX_PORT}")
            return None, None

        return port, host

    def _check_port_connection(self, port, host):
        """Check if port is open on host"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                result = sock.connect_ex((host, port))

                if result == 0:
                    self.success(f"Port {port} is open on {host}")
                    return True
                else:
                    self.error(f"Port {port} is closed on {host}")
                    return False

        except socket.gaierror:
            self.error(f"Could not resolve hostname: {host}")
            return False
        except Exception as e:
            self.error(f"Error checking port: {e}")
            return False

    def _show_automatic_help(self):
        """Show automatic help for port command"""
        actions = [
            {"name": "<port>", "description": "Port number to check (1-65535)"},
            {
                "name": "<port> <host>",
                "description": "Check port on specific host (default: localhost)",
            },
        ]
        self.show_automatic_help(
            "ip:port <port> [host]",
            actions,
            "Check if a port is open on localhost or specified host",
        )


def register_port_command():
    """Register the port command"""
    cmd = PortCommand()
    registry.register(
        name="port",
        description="Check if port is open",
        category="ip",
        func=cmd.execute,
        usage="ip:port <port> [host]",
    )
