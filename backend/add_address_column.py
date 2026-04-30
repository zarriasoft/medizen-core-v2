import os
import sqlite3
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

# Load production env
load_dotenv(".env.production")

# Local SQLite migration
print("Migrating local SQLite db...")
try:
    conn_sqlite = sqlite3.connect("medizen_core.db")
    cursor_sqlite = conn_sqlite.cursor()
    cursor_sqlite.execute("ALTER TABLE patients ADD COLUMN address VARCHAR;")
    conn_sqlite.commit()
    conn_sqlite.close()
    print("Local SQLite migrated successfully.")
except sqlite3.OperationalError as e:
    print(f"SQLite error: {e}")

# Production PostgreSQL migration
print("Migrating production Postgres db...")
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = None

if database_url:
    try:
        conn_pg = psycopg2.connect(database_url)
        cursor_pg = conn_pg.cursor()
        cursor_pg.execute("ALTER TABLE patients ADD COLUMN address VARCHAR;")
        conn_pg.commit()
        conn_pg.close()
        print("Production Postgres migrated successfully.")
    except psycopg2.Error as e:
        print(f"Postgres error: {e}")
else:
    print("DATABASE_URL not found in .env.production")
