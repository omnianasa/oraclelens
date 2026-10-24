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
    
    def list_sequences(self, search: str = "") -> list[dict]:
        sql = """
            SELECT sequence_name
            FROM user_sequences
            WHERE UPPER(sequence_name) LIKE :search
            ORDER BY sequence_name
        """
        return self._fetch_all(
            sql,
            {"search": f"%{search.upper()}%"},
        )

    def list_users(self, search: str = "") -> list[dict]:
        sql = """
            SELECT username, user_id, created
            FROM all_users
            WHERE UPPER(username) LIKE :search
            ORDER BY username
        """
        return self._fetch_all(
            sql,
            {"search": f"%{search.upper()}%"},
        )

    def list_constraints(self, table_name: str) -> list[dict]:
        table_name = validate_identifier(table_name)

        sql = """
            SELECT
                c.constraint_name,
                c.constraint_type,
                c.status,
                cc.column_name,
                cc.position
            FROM user_constraints c
            LEFT JOIN user_cons_columns cc
              ON cc.constraint_name = c.constraint_name
             AND cc.table_name = c.table_name
            WHERE c.table_name = :table_name
            ORDER BY c.constraint_name, cc.position
        """
        return self._fetch_all(
            sql,
            {"table_name": table_name},
        )

    def get_view_definition(self, view_name: str) -> dict:
        view_name = validate_identifier(view_name)

        sql = """
            SELECT view_name, text
            FROM user_views
            WHERE view_name = :view_name
        """
        result = self._fetch_one(
            sql,
            {"view_name": view_name},
        )

        if result is None:
            raise ValueError(f"View not found: {view_name}")

        return result

    def get_sequence_metadata(self, sequence_name: str) -> dict:
        sequence_name = validate_identifier(sequence_name)

        sql = """
            SELECT
                sequence_name,
                min_value,
                max_value,
                increment_by,
                cycle_flag,
                order_flag,
                cache_size,
                last_number
            FROM user_sequences
            WHERE sequence_name = :sequence_name
        """
        result = self._fetch_one(
            sql,
            {"sequence_name": sequence_name},
        )

        if result is None:
            raise ValueError(
                f"Sequence not found: {sequence_name}"
            )

        return result

    def get_user_account_info(self, username: str) -> dict:
        username = validate_identifier(username)

        current_user = self._fetch_one(
            "SELECT USER AS username FROM dual"
        )["username"]

        if username == current_user:
            sql = """
                SELECT
                    username,
                    account_status,
                    created,
                    default_tablespace,
                    temporary_tablespace
                FROM user_users
            """
            result = self._fetch_one(sql)

        else:
            # DBA_USERS requires suitable privileges.
            # We do not attempt to bypass those privileges.
            sql = """
                SELECT
                    username,
                    account_status,
                    created,
                    default_tablespace,
                    temporary_tablespace
                FROM dba_users
                WHERE username = :username
            """
            try:
                result = self._fetch_one(
                    sql,
                    {"username": username},
                )
            except Exception as exc:
                raise PermissionError(
                    "Account details for other users require "
                    "access to DBA_USERS. Ask your DBA for "
                    "appropriate read-only access."
                ) from exc

        if result is None:
            raise ValueError(f"User not found: {username}")

        return result

    def list_user_roles(self, username: str) -> list[dict]:
        username = validate_identifier(username)

        current_user = self._fetch_one(
            "SELECT USER AS username FROM dual"
        )["username"]

        if username == current_user:
            sql = """
                SELECT granted_role, admin_option, default_role
                FROM user_role_privs
                ORDER BY granted_role
            """
            return self._fetch_all(sql)

        sql = """
            SELECT granted_role, admin_option, default_role
            FROM dba_role_privs
            WHERE grantee = :username
            ORDER BY granted_role
        """
        try:
            return self._fetch_all(
                sql,
                {"username": username},
            )
        except Exception as exc:
            raise PermissionError(
                "Roles for other users require access to "
                "DBA_ROLE_PRIVS."
            ) from exc

    def list_user_system_privileges(
        self,
        username: str,
     ) -> list[dict]:
        username = validate_identifier(username)

        current_user = self._fetch_one(
            "SELECT USER AS username FROM dual"
        )["username"]

        if username == current_user:
            sql = """
                SELECT privilege, admin_option
                FROM user_sys_privs
                ORDER BY privilege
            """
            return self._fetch_all(sql)

        sql = """
            SELECT privilege, admin_option
            FROM dba_sys_privs
            WHERE grantee = :username
            ORDER BY privilege
        """
        try:
            return self._fetch_all(
                sql,
                {"username": username},
            )
        except Exception as exc:
            raise PermissionError(
                "System privileges for other users require "
                "access to DBA_SYS_PRIVS."
            ) from exc


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