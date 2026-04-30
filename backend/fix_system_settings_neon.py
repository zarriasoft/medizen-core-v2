import os
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

def fix_system_settings():
    load_dotenv()
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
            inspector = inspect(engine)
            if "system_settings" not in inspector.get_table_names():
                print("Table system_settings does not exist. Creating it...")
                conn.execute(text("""
                    CREATE TABLE system_settings (
                        id SERIAL PRIMARY KEY,
                        smtp_host VARCHAR DEFAULT 'smtp.gmail.com',
                        smtp_port INTEGER DEFAULT 587,
                        smtp_user VARCHAR DEFAULT '',
                        smtp_password VARCHAR DEFAULT '',
                        admin_email VARCHAR DEFAULT '',
                        updated_at TIMESTAMP
                    );
                """))
                conn.commit()
                print("Table system_settings created.")
            else:
                print("Table system_settings exists. Checking columns...")
                columns = [col['name'] for col in inspector.get_columns("system_settings")]

                required_cols = {
                    "smtp_host": "VARCHAR DEFAULT 'smtp.gmail.com'",
                    "smtp_port": "INTEGER DEFAULT 587",
                    "smtp_user": "VARCHAR DEFAULT ''",
                    "smtp_password": "VARCHAR DEFAULT ''",
                    "admin_email": "VARCHAR DEFAULT ''",
                    "updated_at": "TIMESTAMP"
                }

                for col_name, col_def in required_cols.items():
                    if col_name not in columns:
                        conn.execute(text(f"ALTER TABLE system_settings ADD COLUMN {col_name} {col_def};"))
                        print(f"Added column: {col_name}")

                conn.commit()
                print("Schema ensured.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_system_settings()
