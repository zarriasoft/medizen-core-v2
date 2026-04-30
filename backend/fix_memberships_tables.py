import os
import psycopg2
import sys

NEON_URL = os.environ.get("DATABASE_URL")
if not NEON_URL:
    print("ERROR: DATABASE_URL no configurada.")
    sys.exit(1)

def fix_schema():
    print("Connecting to Neon database...")
    try:
        conn = psycopg2.connect(NEON_URL)
        conn.autocommit = True
        cur = conn.cursor()

        # membership_plans
        plan_cols = [
            ("description", "VARCHAR"),
            ("price", "VARCHAR"),
            ("frequency", "VARCHAR"),
            ("features", "VARCHAR"),
            ("color", "VARCHAR DEFAULT 'slate'"),
            ("is_popular", "BOOLEAN DEFAULT FALSE"),
            ("total_sessions", "INTEGER DEFAULT 1"),
            ("is_active", "BOOLEAN DEFAULT TRUE")
        ]

        for col_name, col_type in plan_cols:
            try:
                cur.execute(f"ALTER TABLE membership_plans ADD COLUMN {col_name} {col_type};")
                print(f"Added {col_name} to membership_plans")
            except psycopg2.errors.DuplicateColumn:
                print(f"{col_name} already exists in membership_plans")

        # memberships
        mem_cols = [
            ("membership_type", "VARCHAR"),
            ("total_sessions", "INTEGER DEFAULT 0"),
            ("used_sessions", "INTEGER DEFAULT 0"),
            ("is_active", "BOOLEAN DEFAULT TRUE")
        ]

        # patients
        try:
            cur.execute("ALTER TABLE patients ADD COLUMN hashed_password VARCHAR;")
            print("Added hashed_password to patients")
        except psycopg2.errors.DuplicateColumn:
            print("hashed_password already exists in patients")

        print("Schema fixed successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_schema()
