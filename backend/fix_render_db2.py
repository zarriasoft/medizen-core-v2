import os
import sqlalchemy
from sqlalchemy import create_engine, text

def sync_schema():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    print("Connecting to database...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 1. Update memberships table
            print("Updating memberships table...")
            try:
                conn.execute(text("ALTER TABLE memberships ADD COLUMN total_sessions INTEGER DEFAULT 1;"))
                print("  - Added total_sessions column")
            except sqlalchemy.exc.ProgrammingError as e:
                print("  - total_sessions column already exists or error")
            
            try:
                conn.execute(text("ALTER TABLE memberships ADD COLUMN used_sessions INTEGER DEFAULT 0;"))
                print("  - Added used_sessions column")
            except sqlalchemy.exc.ProgrammingError as e:
                print("  - used_sessions column already exists")
                
            try:
                conn.execute(text("ALTER TABLE memberships ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"))
                print("  - Added is_active column")
            except sqlalchemy.exc.ProgrammingError as e:
                print("  - is_active column already exists")
                
            try:
                conn.execute(text("ALTER TABLE memberships DROP COLUMN amount;"))
                print("  - Dropped amount column")
            except sqlalchemy.exc.ProgrammingError as e:
                print("  - amount column already dropped")
                
            # 2. Update appointments table
            print("Updating appointments table...")
            try:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN membership_id INTEGER;"))
                print("  - Added membership_id column")
            except sqlalchemy.exc.ProgrammingError as e:
                 print("  - membership_id column already exists")

            try:    
                conn.execute(text("ALTER TABLE appointments ADD CONSTRAINT fk_appt_membership FOREIGN KEY (membership_id) REFERENCES memberships(id);"))
                print("  - Added foreign key to appointments")
            except sqlalchemy.exc.ProgrammingError as e:
                 print("  - foreign key already exists")
                 
            conn.commit()
            print("Successfully updated database schema!")
        
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    sync_schema()
