import os
import sys
import psycopg2

NEON_URL = os.environ.get("DATABASE_URL")
if not NEON_URL:
    print("ERROR: DATABASE_URL no configurada.")
    sys.exit(1)

print("Connecting to Neon PostgreSQL...")
try:
    conn = psycopg2.connect(NEON_URL)
    cur = conn.cursor()

    print("Adding 'description' column to membership_plans table...")
    try:
        cur.execute("ALTER TABLE membership_plans ADD COLUMN description VARCHAR;")
        print("  - Added description column successfully")
    except psycopg2.errors.DuplicateColumn:
        print("  - description column already exists")

    conn.commit()
    print("Database schema updated successfully!")

except Exception as e:
    print(f"Error updating database: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
