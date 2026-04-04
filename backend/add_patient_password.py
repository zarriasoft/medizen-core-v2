import sqlite3

def add_password_column():
    conn = sqlite3.connect('medizen_core.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE patients ADD COLUMN hashed_password VARCHAR")
        conn.commit()
        print("Successfully added hashed_password to patients")
    except sqlite3.OperationalError as e:
        print(f"Error (column might already exist): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_password_column()
