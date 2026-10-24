from oraclelens.commands import CommandRouter
from oraclelens.config import OracleLensConfig
from oraclelens.connection import OracleConnectionManager
from oraclelens.explorer import SchemaExplorer
from oraclelens.repository import OracleRepository
from oraclelens.ui import TerminalUI


class OracleLensApplication:
    def __init__(self):
        self.ui = TerminalUI()
        self.config = OracleLensConfig.from_env()
        self.connection_manager = OracleConnectionManager(
            self.config
        )

        self.repository = None
        self.explorer = None
        self.router = CommandRouter(self)

    def run(self) -> None:
        self.ui.welcome()

        try:
            connection = self.connection_manager.connect()
            self.repository = OracleRepository(connection)
            self.explorer = SchemaExplorer(self.repository)

            self.ui.success("Connected to Oracle Database.")
            self.ui.info("Type 'help' to see available commands.")

            self._command_loop()

        except Exception as exc:
            self.ui.error(
                f"Could not start OracleLens: {exc}"
            )

        finally:
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