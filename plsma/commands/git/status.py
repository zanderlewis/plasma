"""
Git status command implementation
"""

from rich.console import Console

from ..base import BaseCommand
from ..registry import registry

console = Console()


class StatusCommand(BaseCommand):
    """Git status utilities"""

    def execute(self, _):
        """Show enhanced git status with branch information"""
        self.info("Git Status Overview")

        # Current branch and upstream
        result = self._run_command("git branch -vv")
        if result.returncode == 0:
            console.print("\n[bold]Branches:[/bold]")
            console.print(result.stdout)

        # Status
        result = self._run_command("git status --porcelain")
        if result.returncode == 0:
            if result.stdout.strip():
                console.print("\n[bold]Changes:[/bold]")
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    status = line[:2]
                    filename = line[3:]
                    if status == "??":
                        console.print(f"[red]  Untracked: {filename}[/red]")
                    elif status[0] == "M":
                        console.print(f"[yellow]  Modified:  {filename}[/yellow]")
                    elif status[0] == "A":
                        console.print(f"[green]  Added:     {filename}[/green]")
                    elif status[0] == "D":
                        console.print(f"[red]  Deleted:   {filename}[/red]")
                    else:
                        console.print(f"[blue]  {status}:        {filename}[/blue]")
            else:
                self.success("Working directory clean")

        # Recent commits
        result = self._run_command("git log --oneline -5")
        if result.returncode == 0:
            console.print("\n[bold]Recent commits:[/bold]")
            console.print(result.stdout)

        return True


def register_status_command():
    """Register the status command"""
    cmd = StatusCommand()
    registry.register(
        name="status",
        description="Enhanced git status with branch info",
        category="git",
        func=cmd.execute,
        usage="git:status",
    )
