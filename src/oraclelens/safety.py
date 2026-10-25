import re


_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9_$#]{0,127}$"
)

_BLOCKED_SQL_WORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "COMMIT",
    "ROLLBACK",
    "EXECUTE",
    "CALL",
    "BEGIN",
    "DECLARE",
}


def validate_identifier(value: str) -> str:
    value = value.strip()

    if not _IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid Oracle identifier: {value!r}")

    return value.upper()


def quote_identifier(value: str) -> str:
    safe_value = validate_identifier(value)
    return f'"{safe_value}"'


def validate_read_query(sql: str) -> str:
    sql = sql.strip()

    if not sql:
        raise ValueError("SQL query cannot be empty.")

    if len(sql) > 20_000:
        raise ValueError("SQL query is too long.")

    # This initial workspace intentionally supports SELECT only.
    if not re.match(r"^SELECT\b", sql, flags=re.IGNORECASE):
        raise ValueError("Only SELECT statements are supported.")

    # Reject statement chaining, comments, and SQL*Plus commands.
    if any(token in sql for token in (";", "--", "/*", "*/")):
        raise ValueError(
            "Semicolons and SQL comments are not supported."
        )

    if sql.startswith("/") or sql.startswith("@"):
        raise ValueError("SQL*Plus commands are not supported.")

    # Conservative first-pass check, not a complete SQL parser.
    words = re.findall(r"[A-Za-z_]+", sql.upper())
    blocked = _BLOCKED_SQL_WORDS.intersection(words)

    if blocked:
        raise ValueError(
            "Potentially unsafe SQL keyword(s): "
            + ", ".join(sorted(blocked))
        )
    if re.search(r"\bFOR\s+UPDATE\b", sql, re.IGNORECASE):
        raise ValueError(
            "SELECT FOR UPDATE is not supported."
        )

    return sql