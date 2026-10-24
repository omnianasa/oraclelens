class SchemaExplorer:
    def __init__(self, repository):
        self.repository = repository

    def list_tables(self, search: str = "") -> list[dict]:
        return self.repository.list_tables(search)

    def list_views(self, search: str = "") -> list[dict]:
        return self.repository.list_views(search)

    def describe(self, table_name: str) -> list[dict]:
        return self.repository.describe_table(table_name)

    def relations(self, table_name: str) -> list[dict]:
        return self.repository.list_relations(table_name)

    def indexes(self, table_name: str) -> list[dict]:
        return self.repository.list_indexes(table_name)

    def show(
        self,
        table_name: str,
        limit: int = 20,
        page: int = 1,
    ) -> list[dict]:
        return self.repository.show_table(
            table_name,
            limit=limit,
            page=page,
        )
    
    def list_sequences(self, search: str = "") -> list[dict]:
        return self.repository.list_sequences(search)

    def list_users(self, search: str = "") -> list[dict]:
        return self.repository.list_users(search)

    def constraints(self, table_name: str) -> list[dict]:
        return self.repository.list_constraints(table_name)

    def view_definition(self, view_name: str) -> dict:
        return self.repository.get_view_definition(view_name)

    def sequence_metadata(self, sequence_name: str) -> dict:
        return self.repository.get_sequence_metadata(sequence_name)

    def user_info(self, username: str) -> dict:
        return self.repository.get_user_account_info(username)

    def user_roles(self, username: str) -> list[dict]:
        return self.repository.list_user_roles(username)

    def user_privileges(self, username: str) -> list[dict]:
        return self.repository.list_user_system_privileges(username)
