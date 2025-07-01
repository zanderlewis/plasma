"""
Server kill command implementation
"""

import psutil
from rich.console import Console

from ..base import BaseCommand
from ..registry import registry

console = Console()


class KillCommand(BaseCommand):
    """Kill processes on specified ports"""

    def execute(self, args):
        """Kill process running on specified port"""
        if not args:
            self.error("Port number required")
            self._show_automatic_help()
            return False

        port = args[0]
        self.info(f"Looking for process on port {port}...")

        try:
            # Find processes using the port
            connections = psutil.net_connections(kind="inet")
            processes_to_kill = []

            for conn in connections:
                if conn.laddr and conn.laddr.port == int(port) and conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        processes_to_kill.append(process)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            if not processes_to_kill:
                self.warning(f"No process found running on port {port}")
                return True

            for process in processes_to_kill:
                try:
                    self.info(f"Found process: {process.name()} (PID: {process.pid})")
                    process.terminate()
                    process.wait(timeout=5)
                    self.success(f"Successfully killed process {process.pid}")
                except psutil.TimeoutExpired:
                    self.warning(
                        f"Process {process.pid} didn't terminate, force killing..."
                    )
                    process.kill()
                    self.success(f"Force killed process {process.pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.error(f"Killing process: {e}")

        except ValueError:
            self.error("Invalid port number")
            return False
        except Exception as e:
            self.error(str(e))
            return False

        return True

    def _show_automatic_help(self):
        """Show automatic help for kill command"""
        actions = [
            {"name": "<port>", "description": "Port number to kill processes on"},
        ]
        self.show_automatic_help(
            "server:kill <port>",
            actions,
            "Kill processes running on the specified port",
        )


def register_kill_command():
    """Register the kill command"""
    cmd = KillCommand()
    registry.register(
        name="kill",
        description="Kill process running on specified port",
        category="server",
        func=cmd.execute,
        usage="server:kill <port>",
    )
