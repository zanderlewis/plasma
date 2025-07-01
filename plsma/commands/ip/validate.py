"""
IP validate command implementation
"""

import ipaddress

from ..base import BaseCommand
from ..registry import registry


class ValidateCommand(BaseCommand):
    """Validate IP addresses"""

    def execute(self, args):
        """Validate if a string is a valid IP address"""
        if not args:
            self.error("IP address required")
            self._show_automatic_help()
            return False

        ip_str = args[0]

        try:
            # Try IPv4
            ipv4 = ipaddress.IPv4Address(ip_str)
            self.success(f"Valid IPv4 address: {ip_str}")

            # Additional info
            if ipv4.is_private:
                self.info("This is a private IP address")
            elif ipv4.is_loopback:
                self.info("This is a loopback IP address")
            elif ipv4.is_link_local:
                self.info("This is a link-local IP address")
            else:
                self.info("This is a public IP address")

            return True

        except ipaddress.AddressValueError:
            try:
                # Try IPv6
                ipv6 = ipaddress.IPv6Address(ip_str)
                self.success(f"Valid IPv6 address: {ip_str}")

                # Additional info
                if ipv6.is_private:
                    self.info("This is a private IPv6 address")
                elif ipv6.is_loopback:
                    self.info("This is a loopback IPv6 address")
                elif ipv6.is_link_local:
                    self.info("This is a link-local IPv6 address")
                else:
                    self.info("This is a global IPv6 address")

                return True

            except ipaddress.AddressValueError:
                self.error(f"Invalid IP address: {ip_str}")
                return False

    def _show_automatic_help(self):
        """Show automatic help for validate command"""
        actions = [
            {"name": "<ip_address>", "description": "IPv4 or IPv6 address to validate"},
        ]
        self.show_automatic_help(
            "ip:validate <ip_address>",
            actions,
            "Validate if a string is a valid IP address (IPv4 or IPv6)",
        )


def register_validate_command():
    """Register the validate command"""
    cmd = ValidateCommand()
    registry.register(
        name="validate",
        description="Validate IP address format",
        category="ip",
        func=cmd.execute,
        usage="ip:validate <ip_address>",
    )
