import sqlite3

def upgrade_db():
    conn = sqlite3.connect('medizen_core.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE membership_plans ADD COLUMN description VARCHAR;")
        print("Column 'description' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error (column might already exist): {e}")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade_db()
