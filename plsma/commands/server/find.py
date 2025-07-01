"""
Server find command implementation
"""

import psutil
from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

# Constants
MAX_PORTS_DISPLAY = 5

console = Console()


class FindCommand(BaseCommand):
    """Find processes by name or port"""

    def execute(self, args):
        """Find processes by name or port"""
        if not args:
            self.error("Search term required")
            self._show_automatic_help()
            return False

        search_term = args[0]
        self.info(f"Searching for processes matching '{search_term}'...")

        try:
            found_processes = self._search_processes(search_term)
            self._display_process_results(search_term, found_processes)
            return True
        except Exception as e:
            self.error(str(e))
            return False

    def _search_processes(self, search_term):
        """Search for processes by name or port"""
        found_processes = []

        # Search by port if it's a number
        if search_term.isdigit():
            found_processes.extend(self._find_processes_by_port(int(search_term)))

        # Search by process name
        found_processes.extend(self._find_processes_by_name(search_term))

        # Remove duplicates while preserving order
        unique_processes = []
        for process in found_processes:
            if process not in unique_processes:
                unique_processes.append(process)

        return unique_processes

    def _find_processes_by_port(self, port):
        """Find processes listening on a specific port"""
        processes = []
        connections = psutil.net_connections(kind="inet")
        for conn in connections:
            if conn.laddr and conn.laddr.port == port and conn.pid:
                try:
                    process = psutil.Process(conn.pid)
                    processes.append(process)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        return processes

    def _find_processes_by_name(self, search_term):
        """Find processes by name matching"""
        processes = []
        for process in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "status"]
        ):
            try:
                if search_term.lower() in process.info["name"].lower():
                    processes.append(process)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def _display_process_results(self, search_term, found_processes):
        """Display process search results in a table"""
        if not found_processes:
            self.warning(f"No processes found matching '{search_term}'")
            return

        table = Table(title=f"Processes matching '{search_term}'")
        table.add_column("PID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("CPU%", style="yellow")
        table.add_column("Memory%", style="red")
        table.add_column("Status", style="blue")
        table.add_column("Ports", style="magenta")

        # Display results (limit to 32)
        for process in found_processes[:32]:
            try:
                ports_str = self._get_process_ports_str(process)
                table.add_row(
                    str(process.pid),
                    process.name(),
                    f"{process.cpu_percent():.1f}%",
                    f"{process.memory_percent():.1f}%",
                    process.status(),
                    ports_str,
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        console.print(table)

    def _get_process_ports_str(self, process):
        """Get formatted string of ports for a process"""
        ports = []
        connections = psutil.net_connections(kind="inet")
        for conn in connections:
            if conn.pid == process.pid and conn.laddr:
                ports.append(str(conn.laddr.port))

        if not ports:
            return "-"

        ports_str = ", ".join(ports[:MAX_PORTS_DISPLAY])
        if len(ports) > MAX_PORTS_DISPLAY:
            ports_str += "..."

        return ports_str

    def _show_automatic_help(self):
        """Show automatic help for find command"""
        actions = [
            {
                "name": "<name_or_port>",
                "description": "Process name or port number to search for",
            },
        ]
        self.show_automatic_help(
            "server:find <name_or_port>",
            actions,
            "Find processes by name or port number",
        )


def register_find_command():
    """Register the find command"""
    cmd = FindCommand()
    registry.register(
        name="find",
        description="Find processes by name or port",
        category="server",
        func=cmd.execute,
        usage="server:find <name_or_port>",
    )
