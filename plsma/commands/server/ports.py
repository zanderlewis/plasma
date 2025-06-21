"""
Server ports command implementation
"""

import psutil
from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

console = Console()


class PortsCommand(BaseCommand):
    """List all listening ports"""

    def execute(self, _):
        """List all listening ports"""
        self.info("Scanning for listening ports...")

        table = Table(title="Listening Ports")
        table.add_column("Port", style="cyan")
        table.add_column("Protocol", style="green")
        table.add_column("Process", style="yellow")
        table.add_column("PID", style="red")
        table.add_column("Status", style="blue")

        try:
            connections = psutil.net_connections(kind="inet")
            listening_ports = {}

            for conn in connections:
                if conn.status == "LISTEN" and conn.laddr:
                    port = conn.laddr.port
                    if port not in listening_ports:
                        try:
                            if conn.pid:
                                process = psutil.Process(conn.pid)
                                process_name = process.name()
                                pid_display = conn.pid
                            else:
                                process_name = "Unknown"
                                pid_display = "N/A"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "Unknown"
                            pid_display = "N/A"

                        listening_ports[port] = {
                            "protocol": "TCP" if conn.type == 1 else "UDP",
                            "process": process_name,
                            "pid": pid_display,
                            "status": conn.status,
                        }

            # Sort ports numerically
            for port in sorted(listening_ports.keys()):
                info = listening_ports[port]
                table.add_row(
                    str(port),
                    info["protocol"],
                    info["process"],
                    str(info["pid"]),
                    info["status"],
                )

            console.print(table)
            self.success(f"Found {len(listening_ports)} listening ports")

        except Exception as e:
            self.error(str(e))
            return False

        return True


def register_ports_command():
    """Register the ports command"""
    cmd = PortsCommand()
    registry.register(
        name="ports",
        description="List all listening ports",
        category="server",
        func=cmd.execute,
        usage="server:ports",
    )
