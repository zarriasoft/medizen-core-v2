import os
import psycopg2

def sync_schema():
    # Prompting the user to run this with their actual DATABASE_URL since we don't have it locally
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        print("Please run this script like this:")
        print("  set DATABASE_URL=postgresql://your_user:your_password@your_host/your_db")
        print("  python fix_render_db.py")
        return

    print("Connecting to database...")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 1. Update memberships table
        print("Updating memberships table...")
        
        try:
            cur.execute("ALTER TABLE memberships ADD COLUMN total_sessions INTEGER DEFAULT 1;")
            print("  - Added total_sessions column")
        except psycopg2.errors.DuplicateColumn:
            print("  - total_sessions column already exists")
            conn.rollback() # reset tx
            
        try:
            cur.execute("ALTER TABLE memberships ADD COLUMN used_sessions INTEGER DEFAULT 0;")
            print("  - Added used_sessions column")
        except psycopg2.errors.DuplicateColumn:
            print("  - used_sessions column already exists")
            conn.rollback()
            
        try:
            cur.execute("ALTER TABLE memberships ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
            print("  - Added is_active column")
        except psycopg2.errors.DuplicateColumn:
            print("  - is_active column already exists")
            conn.rollback()
            
        try:
            cur.execute("ALTER TABLE memberships DROP COLUMN amount;")
            print("  - Dropped amount column")
        except psycopg2.errors.UndefinedColumn:
            print("  - amount column already dropped")
            conn.rollback()
            
        # 2. Update appointments table
        print("Updating appointments table...")
        try:
            cur.execute("ALTER TABLE appointments ADD COLUMN membership_id INTEGER;")
            cur.execute("ALTER TABLE appointments ADD CONSTRAINT fk_appt_membership FOREIGN KEY (membership_id) REFERENCES memberships(id);")
            print("  - Added membership_id column and foreign key")
        except psycopg2.errors.DuplicateColumn:
             print("  - membership_id column already exists")
             conn.rollback()
             
        # Commit the changes
        conn.commit()
        print("Successfully updated database schema!")
        
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sync_schema()
