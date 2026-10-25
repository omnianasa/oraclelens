# OracleLens 

**An Object-Oriented Oracle Database Terminal Explorer built with Python.**

OracleLens is a command-line application for exploring Oracle Database metadata and browsing table data directly from the terminal. It provides a simple interface for inspecting tables, views, columns, constraints, indexes, sequences, users, roles, and privileges without needing to write a separate SQL query for every metadata operation.

## Getting Started

### Prerequisites

- Python 3.12 or later
- Access to an Oracle Database
- A valid Oracle database username and password
- Network access to the configured database service

##### Clone the repository

```bash
git clone https://github.com/omnianasa/oraclelens
cd oraclelens
```

##### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

##### Install OracleLens

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Editable installation makes the `oraclelens` command available in the active environment when the project entry point is configured correctly.

##### Configure the database connection

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Set the connection details in `.env`:

```dotenv
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:8521/FREEPDB1
```

##### Launch OracleLens

```bash
oraclelens
```

Alternatively, run the application as a Python module:

```bash
python -m oraclelens.main
```

If the connection succeeds, OracleLens displays its interactive prompt.

#### Command Reference

| Command | Description |
|---|---|
| `help` | Show available commands |
| `status` | Test the database connection |
| `tables [search]` | List tables, optionally filtered |
| `views [search]` | List views, optionally filtered |
| `describe TABLE` | Show column information |
| `relations TABLE` | Show foreign-key relationships |
| `indexes TABLE` | Show indexes and indexed columns |
| `show TABLE [--limit N] [--page N]` | Browse table rows with pagination |
| `query SELECT ...` | Execute a read-only SQL query |
| `sequences [search]` | List sequences, optionally filtered |
| `sequence-info NAME` | Show sequence properties |
| `users [search]` | List database users, optionally filtered |
| `user-info NAME` | Show account information |
| `user-roles NAME` | Show roles granted to a user |
| `user-privileges NAME` | Show system privileges granted to a user |
| `constraints TABLE` | Show table constraints |
| `view-definition VIEW` | Show a view's SQL definition |
| `clear` | Clear the terminal |
| `exit` | Exit OracleLens |

**Note:** Metadata visibility depends on the connected Oracle account and its privileges. Some commands may return empty results or permission errors when the account cannot access the relevant metadata.

---