"""
IP ping command implementation
"""

from ..base import BaseCommand
from ..registry import registry


class PingCommand(BaseCommand):
    """Ping utilities"""

    def execute(self, args):
        """Ping a host"""
        if not args:
            self.error("Host required")
            self._show_automatic_help()
            return False

        host = args[0]
        count = "4"  # Default ping count

        if len(args) > 1:
            try:
                count = str(int(args[1]))
            except ValueError:
                self.warning(f"Invalid count '{args[1]}', using default: 4")
                count = "4"

        self.info(f"Pinging {host} with {count} packets...")

        # Use system ping command
        result = self._run_command(f"ping -c {count} {host}", capture_output=False)

        if result.returncode == 0:
            self.success(f"Ping to {host} successful")
        else:
            self.error(f"Ping to {host} failed")

        return result.returncode == 0

    def _show_automatic_help(self):
        """Show automatic help for ping command"""
        actions = [
            {"name": "<host>", "description": "Host to ping (IP address or hostname)"},
            {
                "name": "<host> <count>",
                "description": "Host to ping with custom packet count",
            },
        ]
        self.show_automatic_help(
            "ip:ping <host> [count]",
            actions,
            "Ping a host with configurable packet count",
        )


def register_ping_command():
    """Register the ping command"""
    cmd = PingCommand()
    registry.register(
        name="ping",
        description="Ping a host",
        category="ip",
        func=cmd.execute,
        usage="ip:ping <host> [count]",
    )
