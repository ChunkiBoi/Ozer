#!/usr/bin/env python3

# Script uses:
#   Initialize the database for the first time,
#   creating the necessary tables and relationships.
#
#   Update the database schema if needed after changes to
#   `schema.sql` by applying migrations or altering tables.
#   WARNING: This script will clear existing data.
#
#   Clear the database by dropping all tables and recreating them.
#   WARNING: This script will clear existing data.

# AI assistance disclosure: GitHub Copilot helped explain and review this
# SQLite initialization script and its relationship to schema.sql.

import sqlite3
from pathlib import Path

project_dir = Path(__file__).resolve().parent
database_path = project_dir / "ozer.db"
schema_path = project_dir / "schema.sql"

with sqlite3.connect(database_path) as db:
    db.execute("PRAGMA foreign_keys = ON")

    with schema_path.open(encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())
