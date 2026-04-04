import sqlite3
import smtplib
from smtplib import SMTP_SSL
from email.message import EmailMessage

db_path = "C:/Medizen/v2/backend/medizen_core.db"

def test_smtp():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT smtp_host, smtp_port, smtp_user, smtp_password, admin_email FROM system_settings LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            print("No settings found in the database. Table is empty.")
            return

        smtp_host, smtp_port, smtp_user, smtp_password, admin_email = row
        print(f"Loaded from DB:")
        print(f"Host: {smtp_host}")
        print(f"Port: 465 (Overriding {smtp_port} to test SSL directly)")
        print(f"User: {smtp_user}")
        password_masked = "****" if smtp_password else "None"
        print(f"Pass: {password_masked}")
        
        if not all([smtp_host, smtp_user, smtp_password]):
            print("Missing some SMTP credentials. Cannot test.")
            return

        print("\nAttempting SMTP_SSL login on port 465...")
        server = SMTP_SSL(smtp_host, 465, timeout=10)
        server.set_debuglevel(1)
        server.login(smtp_user, smtp_password)
        print("SMTP Login Successful!")
        server.quit()
        
    except Exception as e:
        print(f"SMTP Test Failed: {e}")

if __name__ == '__main__':
    test_smtp()
