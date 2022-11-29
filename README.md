# pilgrimor
Database migration tool with versioning
for python projects

## Installation:

### with pip
```
pip install pilgrimor
```

### with poetry
```
poetry add pilgrimor
```

## Usage:

### Main commands:
* `initdb` - create technical migrations table.
* `apply` - apply new migrations.
* `apply —-version <version number>` - apply new migrations with version.
* `rollback —-version <version number>`- rollback migrations to version inclusive.
* `rollback —-latest` - rollback to latest version.

### Necessary things
You need to specify some fields in your pyproject.toml
```
[tool.pilgrimor]
migrations_dir = "./migrations/"
database_engine = "PSQL"
env_file = "./.env"
```
migrations_dir - folder with migrations
database_engine - there is only one database engine PSQL
env_file = path to .env file

### Migration file structure:
Migration file contains two blocks - apply and rollback with sql commands.
For example:
```
—- apply —-
SQL CODE

—- rollback —-
SQL CODE
```

