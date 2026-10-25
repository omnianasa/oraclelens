from oraclelens.commands import CommandRouter
from oraclelens.config import OracleLensConfig
from oraclelens.connection import OracleConnectionManager
from oraclelens.explorer import SchemaExplorer
from oraclelens.repository import OracleRepository
from oraclelens.ui import TerminalUI


class OracleLensApplication:
    def __init__(self):
        self.ui = TerminalUI()
        self.config = None
        self.connection_manager = None
        self.repository = None
        self.explorer = None

        self.router = CommandRouter(self)

    def run(self) -> None:
        self.ui.welcome()

        try:
            # Ask the user for database credentials.
            self.config = OracleLensConfig.from_prompt()

            # Create the connection manager using the entered credentials.
            self.connection_manager = OracleConnectionManager(
                self.config
            )

            # Connect to Oracle Database.
            connection = self.connection_manager.connect()

            self.repository = OracleRepository(connection)
            self.explorer = SchemaExplorer(self.repository)

            self.ui.success("Connected to Oracle Database.")
            self.ui.info("Type 'help' to see available commands.")

            self._command_loop()

        except KeyboardInterrupt:
            self.ui.info("\nConnection setup cancelled.")

        except Exception as exc:
            self.ui.error(f"Could not start OracleLens: {exc}")

        finally:
            if self.connection_manager is not None:
                self.connection_manager.close()
                self.ui.info("Database connection closed.")

    def _command_loop(self) -> None:
        while True:
            try:
                command = self.ui.prompt()

                if not self.router.execute(command):
                    break

            except KeyboardInterrupt:
                self.ui.info("\nUse 'exit' to quit.")

            except EOFError:
                break

    def show_status(self) -> None:
        result = self.repository.test_connection()
        self.ui.show_records([result], "Connection Status")

    def list_tables(self, search: str = "") -> None:
        records = self.explorer.list_tables(search)
        self.ui.show_records(records, "Tables")

    def list_views(self, search: str = "") -> None:
        records = self.explorer.list_views(search)
        self.ui.show_records(records, "Views")

    def describe(self, table_name: str) -> None:
        records = self.explorer.describe(table_name)
        self.ui.show_records(records, f"Columns: {table_name}")

    def show_relations(self, table_name: str) -> None:
        records = self.explorer.relations(table_name)
        self.ui.show_records(records, f"Relations: {table_name}")

    def show_indexes(self, table_name: str) -> None:
        records = self.explorer.indexes(table_name)
        self.ui.show_records(records, f"Indexes: {table_name}")

    def show_table(
        self,
        table_name: str,
        limit: int = 20,
        page: int = 1,
    ) -> None:
        records = self.explorer.show(
            table_name,
            limit=limit,
            page=page,
        )
        self.ui.show_records(records, f"Data: {table_name}")

    def run_query(self, sql: str) -> None:
        records = self.repository.execute_read_query(sql)
        self.ui.show_records(records, "Query Results")

    def list_sequences(self, search: str = "") -> None:
        records = self.explorer.list_sequences(search)
        self.ui.show_records(records, "Sequences")

    def list_users(self, search: str = "") -> None:
        records = self.explorer.list_users(search)
        self.ui.show_records(records, "Database Users")

    def show_constraints(self, table_name: str) -> None:
        records = self.explorer.constraints(table_name)
        self.ui.show_records(
            records,
            f"Constraints: {table_name}",
        )

    def show_view_definition(self, view_name: str) -> None:
        result = self.explorer.view_definition(view_name)
        definition = result.get("text")

        if definition is None:
            self.ui.info("No view definition returned.")
            return

        self.ui.console.print(
            f"[bold cyan]View: {view_name}[/bold cyan]"
        )
        self.ui.console.print(str(definition))

    def show_sequence_metadata(self, sequence_name: str) -> None:
        result = self.explorer.sequence_metadata(sequence_name)
        self.ui.show_records(
            [result],
            f"Sequence: {sequence_name}",
        )

    def show_user_info(self, username: str) -> None:
        result = self.explorer.user_info(username)
        self.ui.show_records([result], f"User: {username}")

    def show_user_roles(self, username: str) -> None:
        records = self.explorer.user_roles(username)
        self.ui.show_records(records, f"Roles: {username}")

    def show_user_privileges(self, username: str) -> None:
        records = self.explorer.user_privileges(username)
        self.ui.show_records(
            records,
            f"System Privileges: {username}",
        )
