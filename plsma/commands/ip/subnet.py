"""
IP subnet command implementation
"""

import ipaddress

from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

console = Console()


class SubnetCommand(BaseCommand):
    """Subnet information utilities"""

    def execute(self, args):
        """Get subnet information for an IP/CIDR"""
        if not args:
            self.error("IP/CIDR required")
            self._show_automatic_help()
            return False

        cidr_str = args[0]

        try:
            # Try to parse as network
            network = ipaddress.ip_network(cidr_str, strict=False)

            table = Table(title=f"Subnet Information: {network}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Network Address", str(network.network_address))
            table.add_row("Broadcast Address", str(network.broadcast_address))
            table.add_row("Netmask", str(network.netmask))
            table.add_row("Host Mask", str(network.hostmask))
            table.add_row("Number of Hosts", str(network.num_addresses - 2))
            table.add_row("First Host", str(network.network_address + 1))
            table.add_row("Last Host", str(network.broadcast_address - 1))
            table.add_row("CIDR Notation", str(network))

            console.print(table)
            return True

        except Exception as e:
            self.error(f"Invalid network format: {e}")
            return False

    def _show_automatic_help(self):
        """Show automatic help for subnet command"""
        actions = [
            {
                "name": "<ip/cidr>",
                "description": "IP address with CIDR notation (e.g., 192.168.1.0/24)",
            },
        ]
        self.show_automatic_help(
            "ip:subnet <ip/cidr>",
            actions,
            "Get detailed subnet information for an IP/CIDR block",
        )


def register_subnet_command():
    """Register the subnet command"""
    cmd = SubnetCommand()
    registry.register(
        name="subnet",
        description="Get subnet information for IP/CIDR",
        category="ip",
        func=cmd.execute,
        usage="ip:subnet <ip/cidr>",
    )
