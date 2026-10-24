from oraclelens.safety import (
    quote_identifier,
    validate_identifier,
    validate_read_query,
)


class OracleRepository:
    def __init__(self, connection):
        self.connection = connection

    def _fetch_all(self, sql: str, params: dict | None = None):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            columns = [
                column[0].lower()
                for column in cursor.description
            ]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

    def _fetch_one(self, sql: str, params: dict | None = None):
        rows = self._fetch_all(sql, params)
        return rows[0] if rows else None

    def test_connection(self) -> dict:
        result = self._fetch_one(
            "SELECT USER AS username, "
            "SYS_CONTEXT('USERENV', 'DB_NAME') AS database_name "
            "FROM dual"
        )
        return result or {}

    def list_tables(self, search: str = "") -> list[dict]:
        sql = """
            SELECT table_name
            FROM user_tables
            WHERE UPPER(table_name) LIKE :search
            ORDER BY table_name
        """
        return self._fetch_all(
            sql,
            {"search": f"%{search.upper()}%"},
        )

    def list_views(self, search: str = "") -> list[dict]:
        sql = """
            SELECT view_name
            FROM user_views
            WHERE UPPER(view_name) LIKE :search
            ORDER BY view_name
        """
        return self._fetch_all(
            sql,
            {"search": f"%{search.upper()}%"},
        )

    def describe_table(self, table_name: str) -> list[dict]:
        table_name = validate_identifier(table_name)

        sql = """
            SELECT
                column_name,
                data_type,
                data_length,
                nullable,
                data_precision,
                data_scale
            FROM user_tab_columns
            WHERE table_name = :table_name
            ORDER BY column_id
        """
        rows = self._fetch_all(
            sql,
            {"table_name": table_name},
        )

        if not rows:
            raise ValueError(
                f"Table or view not found: {table_name}"
            )

        return rows

    def list_relations(self, table_name: str) -> list[dict]:
        table_name = validate_identifier(table_name)

        sql = """
            SELECT
                c.constraint_name,
                c.table_name,
                cc.column_name,
                c.r_constraint_name AS referenced_constraint,
                parent.table_name AS referenced_table
            FROM user_constraints c
            JOIN user_cons_columns cc
              ON cc.constraint_name = c.constraint_name
             AND cc.table_name = c.table_name
            LEFT JOIN user_constraints parent
              ON parent.constraint_name = c.r_constraint_name
            WHERE c.constraint_type = 'R'
              AND c.table_name = :table_name
            ORDER BY c.constraint_name, cc.position
        """
        return self._fetch_all(
            sql,
            {"table_name": table_name},
        )

    def list_indexes(self, table_name: str) -> list[dict]:
        table_name = validate_identifier(table_name)

        sql = """
            SELECT
                i.index_name,
                i.uniqueness,
                ic.column_name,
                ic.column_position
            FROM user_indexes i
            JOIN user_ind_columns ic
              ON ic.index_name = i.index_name
             AND ic.table_name = i.table_name
            WHERE i.table_name = :table_name
            ORDER BY i.index_name, ic.column_position
        """
        return self._fetch_all(
            sql,
            {"table_name": table_name},
        )

    def show_table(
        self,
        table_name: str,
        limit: int = 20,
        page: int = 1,
    ) -> list[dict]:
        table = quote_identifier(table_name)

        if not 1 <= limit <= 500:
            raise ValueError("Limit must be between 1 and 500.")

        if page < 1:
            raise ValueError("Page must be at least 1.")

        # Verify that the object is a table or view accessible
        # through the current user's schema.
        self.describe_table(table_name)

        offset = (page - 1) * limit

        sql = f"""
            SELECT *
            FROM {table}
            ORDER BY 1
            OFFSET :offset ROWS
            FETCH NEXT :limit ROWS ONLY
        """

        return self._fetch_all(
            sql,
            {"offset": offset, "limit": limit},
        )

    def execute_read_query(self, sql: str) -> list[dict]:
        safe_sql = validate_read_query(sql)
        return self._fetch_all(safe_sql)