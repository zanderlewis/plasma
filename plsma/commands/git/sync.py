"""
Git sync command implementation
"""

from rich.console import Console

from ..base import BaseCommand
from ..registry import registry

console = Console()


class SyncCommand(BaseCommand):
    """Git sync utilities"""

    def execute(self, _):
        """Sync current branch with remote"""
        self.info("Syncing with remote...")

        # Get current branch
        result = self._run_command("git branch --show-current")
        if result.returncode != 0:
            self.error("Not in a git repository")
            return False

        current_branch = result.stdout.strip()
        console.print(f"Current branch: [cyan]{current_branch}[/cyan]")

        # Fetch latest changes
        self.info("Fetching latest changes...")
        result = self._run_command("git fetch origin")
        if result.returncode != 0:
            self.error("Fetching from remote")
            return False

        # Check if remote branch exists
        result = self._run_command(f"git rev-parse --verify origin/{current_branch}")
        if result.returncode != 0:
            self.warning(f"Remote branch origin/{current_branch} does not exist")
            return True

        # Pull changes
        self.info("Pulling changes...")
        result = self._run_command(f"git pull origin {current_branch}")
        if result.returncode == 0:
            self.success("Successfully synced with remote")
        else:
            self.error("Syncing with remote")
            console.print(result.stderr)
            return False

        return True


def register_sync_command():
    """Register the sync command"""
    cmd = SyncCommand()
    registry.register(
        name="sync",
        description="Sync current branch with remote",
        category="git",
        func=cmd.execute,
        usage="git:sync",
    )
