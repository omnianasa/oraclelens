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