from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class TerminalUI:
    def __init__(self):
        self.console = Console()

    def welcome(self) -> None:
        self.console.print(
            Panel(
                "[bold cyan]OracleLens[/bold cyan]\n"
                "Oracle Database Terminal Explorer",
                border_style="cyan",
            )
        )

    def info(self, message: str) -> None:
        self.console.print(f"[cyan]ℹ[/cyan] {message}")

    def success(self, message: str) -> None:
        self.console.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        self.console.print(f"[red]Error:[/red] {message}")

    def show_help(self) -> None:
        commands = [
            ("help", "Show available commands"),
            ("status", "Test the database connection"),
            ("tables [search]", "List tables, optionally filtered"),
            ("views [search]", "List views, optionally filtered"),
            ("describe TABLE", "Show column information"),
            ("relations TABLE", "Show foreign-key relationships"),
            ("indexes TABLE", "Show indexes and indexed columns"),
            ("show TABLE [--limit N] [--page N]", "Browse table rows"),
            ("query SELECT ...", "Execute a read query"),
            ("clear", "Clear the terminal"),
            ("exit", "Exit OracleLens"),
        ]

        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description")

        for command, description in commands:
            table.add_row(command, description)

        self.console.print(table)

    def show_records(
        self,
        records: list[dict],
        title: str = "Results",
    ) -> None:
        if not records:
            self.info("No results found.")
            return

        table = Table(title=title, show_lines=False)

        columns = list(records[0].keys())

        for column in columns:
            table.add_column(str(column), overflow="fold")

        for record in records:
            table.add_row(
                *[
                    self._format_value(record.get(column))
                    for column in columns
                ]
            )

        self.console.print(table)
        self.info(f"{len(records)} row(s) displayed.")

    @staticmethod
    def _format_value(value) -> str:
        if value is None:
            return "NULL"

        text = str(value)

        if len(text) > 200:
            return text[:197] + "..."

        return text

    def prompt(self) -> str:
        return self.console.input("[bold cyan]oraclelens> [/bold cyan]")

    def clear(self) -> None:
        self.console.clear()