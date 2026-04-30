
import sqlite3
import os

db_path = 'c:/Medizen/v2/backend/medizen_core.db'
if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")
        if not cursor.fetchone():
            print("❌ Table system_settings does not exist in SQLite.")
        else:
            rows = conn.execute("SELECT smtp_host, smtp_user, smtp_password, admin_email FROM system_settings").fetchall()
            print(f"--- SYSTEM SETTINGS (SQLite) ---")
            for row in rows:
                print(f"Host: {row[0]}, User: {row[1]}, Pass: {'***' if row[2] else 'None'}, Admin: {row[3]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
