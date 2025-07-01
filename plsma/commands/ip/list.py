"""
IP list command implementation
"""

import ipaddress
import re
import socket

from rich.console import Console
from rich.table import Table

from ..base import BaseCommand
from ..registry import registry

console = Console()


class ListCommand(BaseCommand):
    """List local IP addresses"""

    def execute(self, _):
        """Get local IP addresses"""
        table = Table(title="Local IP Addresses")
        table.add_column("Interface", style="cyan")
        table.add_column("IP Address", style="green")
        table.add_column("Type", style="yellow")

        try:
            # Method 1: Using socket to get primary local IP
            try:
                # Connect to a dummy address to get the local IP used for routing
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    table.add_row("Primary", local_ip, "IPv4 (Local)")
            except Exception:
                pass

            # Method 2: Using system commands to get all interfaces
            try:
                # Use ifconfig on macOS/Linux
                result = self._run_command("ifconfig")
                if result.returncode == 0:
                    self._parse_ifconfig_output(result.stdout, table)
                else:
                    # Fallback to ip command on Linux
                    result = self._run_command("ip addr show")
                    if result.returncode == 0:
                        self._parse_ip_output(result.stdout, table)
            except Exception as e:
                self.warning(f"Could not get interface details: {e}")

            # Method 3: Localhost
            table.add_row("Localhost", "127.0.0.1", "IPv4 (Loopback)")
            table.add_row("Localhost", "::1", "IPv6 (Loopback)")

            console.print(table)
            return True

        except Exception as e:
            self.error(f"Failed to get IP addresses: {e}")
            return False

    def _parse_ifconfig_output(self, output, table):
        """Parse ifconfig output to extract IP addresses"""
        current_interface = None
        lines = output.split("\n")

        for line in lines:
            # Check for interface name
            if line and not line.startswith(" ") and not line.startswith("\t"):
                # Extract interface name (everything before first colon)
                interface_match = re.match(r"^([^:]+)", line)
                if interface_match:
                    current_interface = interface_match.group(1)

            # Look for inet addresses
            if "inet " in line and current_interface:
                # Extract IPv4 address
                ipv4_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                if ipv4_match:
                    ip = ipv4_match.group(1)
                    if ip != "127.0.0.1":  # Skip localhost as we add it separately
                        ip_type = self._classify_ip(ip)
                        table.add_row(current_interface, ip, ip_type)

            # Look for inet6 addresses
            if "inet6 " in line and current_interface:
                # Extract IPv6 address
                ipv6_match = re.search(r"inet6 ([a-fA-F0-9:]+)", line)
                if ipv6_match:
                    ip = ipv6_match.group(1)
                    if ip != "::1":  # Skip localhost as we add it separately
                        ip_type = "IPv6"
                        if ip.startswith("fe80"):
                            ip_type += " (Link-local)"
                        table.add_row(current_interface, ip, ip_type)

    def _parse_ip_output(self, output, table):
        """Parse 'ip addr show' output to extract IP addresses"""
        current_interface = None
        lines = output.split("\n")

        for line in lines:
            # Check for interface name
            if re.match(r"^\d+:", line):
                interface_match = re.search(r"^\d+: ([^:@]+)", line)
                if interface_match:
                    current_interface = interface_match.group(1)

            # Look for inet addresses
            if "inet " in line and current_interface:
                ipv4_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                if ipv4_match:
                    ip = ipv4_match.group(1)
                    if ip != "127.0.0.1":
                        ip_type = self._classify_ip(ip)
                        table.add_row(current_interface, ip, ip_type)

            # Look for inet6 addresses
            if "inet6 " in line and current_interface:
                ipv6_match = re.search(r"inet6 ([a-fA-F0-9:]+)", line)
                if ipv6_match:
                    ip = ipv6_match.group(1)
                    if ip != "::1":
                        ip_type = "IPv6"
                        if ip.startswith("fe80"):
                            ip_type += " (Link-local)"
                        table.add_row(current_interface, ip, ip_type)

    def _classify_ip(self, ip):
        """Classify IP address type"""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            if ip_obj.is_private:
                return "IPv4 (Private)"
            elif ip_obj.is_loopback:
                return "IPv4 (Loopback)"
            elif ip_obj.is_link_local:
                return "IPv4 (Link-local)"
            else:
                return "IPv4 (Public)"
        except (ipaddress.AddressValueError, ValueError):
            return "IPv4"


def register_list_command():
    """Register the list command"""
    cmd = ListCommand()
    registry.register(
        name="list",
        description="Show local IP addresses",
        category="ip",
        func=cmd.execute,
        usage="ip:list",
    )
