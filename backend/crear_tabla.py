import sqlite3
import datetime

def fix_db():
    print("Forzando la creación de la tabla de seguridad en la base de datos...")
    try:
        conn = sqlite3.connect("medizen_core.db")
        cursor = conn.cursor()

        # Crear la tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_locks (
            id INTEGER PRIMARY KEY,
            last_locked_at DATETIME
        )
        """)

        # Insertar la fila inicial necesaria
        cursor.execute("INSERT OR IGNORE INTO booking_locks (id, last_locked_at) VALUES (1, ?)", (datetime.datetime.utcnow(),))

        conn.commit()
        conn.close()
        print("¡Tabla creada con éxito!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
