"""
License command implementation for creating license files
"""

import os

from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..base import BaseCommand
from ..registry import registry
from .licenses import LICENSES

console = Console()


class LicenseCommand(BaseCommand):
    """Create license files for projects"""

    def execute(self, args):
        """Create a license file with the specified license type"""

        # Create a mapping for easier lookup
        license_map = {license["identifier"]: license for license in LICENSES}

        # Parse arguments
        if args and args[0] in license_map:
            license_type = args[0]
        else:
            # Show available licenses and prompt for selection
            self.info("Available licenses:")
            for license_info in LICENSES:
                console.print(
                    f"  [cyan]{license_info['identifier']}[/cyan] - {license_info['name']}"
                )

            # Prompt user to select a license
            license_type = Prompt.ask(
                "Select a license", choices=list(license_map.keys())
            )

        # Check if LICENSE file already exists
        license_file = "LICENSE"
        if os.path.exists(license_file):
            if not Confirm.ask(
                "[yellow]LICENSE file already exists. Overwrite?[/yellow]"
            ):
                self.info("License creation cancelled")
                return True

        # Get license template
        license_template = license_map.get(license_type)
        if not license_template:
            self.error(f"License type '{license_type}' not found")
            return False

        # Generate license content from template
        license_content = license_template["content"]

        # Write license file
        try:
            with open(license_file, "w", encoding="utf-8") as f:
                f.write(license_content)

            self.success(f"Created {license_template['name']} in LICENSE file")

        except Exception as e:
            self.error(f"Failed to create license file: {e}")
            return False

        return True

    def _get_author_name(self):
        """Try to get author name from git config"""
        try:
            result = self._run_command("git config user.name")
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None


def register_license_command():
    """Register the license command"""
    cmd = LicenseCommand()
    registry.register(
        name="license",
        description="Create a license file for your project",
        category="project",
        func=cmd.execute,
        usage="project:license [license_identifier]",
    )
