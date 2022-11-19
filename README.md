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
* `apply —version <version number>` - apply new migrations with version.
* `rollback —version <version number>`- rollback migrations to version inclusive.
* `rollback —latest` - rollback to latest version.

### Migration directory:
Create a separate directory in the project for migration files.
For exemple:
```
./migrations
```

### Migration file structure:
Migration file contains two blocks - apply and rollback with sql commands.
For example:
```
— apply —
SQL CODE

— rollback —
SQL CODE 
```

