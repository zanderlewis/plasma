"""
Git undo command implementation
"""

from rich.console import Console

from ..base import BaseCommand
from ..registry import registry

console = Console()


class UndoCommand(BaseCommand):
    """Git undo utilities"""

    def execute(self, _):
        """Undo the last commit but keep changes"""
        self.info("Undoing last commit (keeping changes)...")

        # Check if we're in a git repository
        repo_check = self._run_command("git rev-parse --git-dir")
        if repo_check.returncode != 0:
            self.error("Not in a git repository")
            return False

        # Check if there are any commits
        commit_check = self._run_command("git log --oneline -1")
        if commit_check.returncode != 0:
            self.error("No commits found in repository")
            return False

        # Check if there's more than one commit
        commit_count = self._run_command("git rev-list --count HEAD")
        if commit_count.returncode != 0:
            self.error("Unable to check commit history")
            return False

        num_commits = int(commit_count.stdout.strip())

        # Show last commit
        console.print(f"Last commit: [cyan]{commit_check.stdout.strip()}[/cyan]")

        if num_commits == 1:
            self.warning("This is the only commit in the repository")
            if self.ask_confirmation(
                "Delete the entire commit history and keep files?"
            ):
                # For the first commit, we need to delete the .git/refs/heads/main file
                # and reset to an empty repository state
                result = self._run_command("git update-ref -d HEAD")
                if result.returncode == 0:
                    self.success("Repository reset to initial state (files preserved)")
                else:
                    self.error(f"Failed to reset repository: {result.stderr.strip()}")
                    return False
        elif self.ask_confirmation("Undo this commit?"):
            result = self._run_command("git reset --soft HEAD~1")
            if result.returncode == 0:
                self.success("Last commit undone (changes preserved)")
            else:
                self.error(f"Failed to undo commit: {result.stderr.strip()}")
                return False

        return True


def register_undo_command():
    """Register the undo command"""
    cmd = UndoCommand()
    registry.register(
        name="undo",
        description="Undo the last commit (keep changes)",
        category="git",
        func=cmd.execute,
        usage="git:undo",
    )
