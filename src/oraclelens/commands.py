import shlex


class CommandRouter:
    def __init__(self, app):
        self.app = app

    def execute(self, raw_command: str) -> bool:
        raw_command = raw_command.strip()

        if not raw_command:
            return True

        # Keep SQL text intact instead of splitting its quotes.
        first_word = raw_command.split(maxsplit=1)[0].lower()

        if first_word == "query":
            sql = raw_command[len("query"):].strip()
            self.app.run_query(sql)
            return True

        try:
            args = shlex.split(raw_command)
        except ValueError as exc:
            self.app.ui.error(f"Invalid command syntax: {exc}")
            return True

        command = args[0].lower()
        values = args[1:]

        try:
            if command == "help":
                self.app.ui.show_help()

            elif command == "status":
                self.app.show_status()

            elif command == "tables":
                self.app.list_tables(self._search(values))

            elif command == "views":
                self.app.list_views(self._search(values))

            elif command == "describe":
                self._require_count(values, 1)
                self.app.describe(values[0])

            elif command == "relations":
                self._require_count(values, 1)
                self.app.show_relations(values[0])

            elif command == "indexes":
                self._require_count(values, 1)
                self.app.show_indexes(values[0])

            elif command == "show":
                self._show_table(values)

            elif command == "clear":
                self.app.ui.clear()

            elif command in {"exit", "quit"}:
                return False

            else:
                self.app.ui.error(
                    f"Unknown command: {command}. Type 'help'."
                )

        except (ValueError, KeyError) as exc:
            self.app.ui.error(str(exc))

        return True

    @staticmethod
    def _require_count(values: list[str], count: int) -> None:
        if len(values) != count:
            raise ValueError(
                f"Expected {count} argument(s), got {len(values)}."
            )

    @staticmethod
    def _search(values: list[str]) -> str:
        if not values:
            return ""

        if len(values) == 2 and values[0] == "--search":
            return values[1]

        if len(values) == 1 and not values[0].startswith("--"):
            return values[0]

        raise ValueError("Use: tables [search] or tables --search NAME")

    def _show_table(self, values: list[str]) -> None:
        if not values:
            raise ValueError(
                "Usage: show TABLE [--limit N] [--page N]"
            )

        table_name = values[0]
        limit = 20
        page = 1

        if (len(values) - 1) % 2 != 0:
            raise ValueError("Options must have a value.")

        options = values[1:]

        for index in range(0, len(options), 2):
            option = options[index]
            value = options[index + 1]

            if option == "--limit":
                limit = int(value)
            elif option == "--page":
                page = int(value)
            else:
                raise ValueError(f"Unknown option: {option}")

        self.app.show_table(
            table_name,
            limit=limit,
            page=page,
        )