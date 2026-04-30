import sqlite3
import os

def check():
    print("========================================")
    print("🩺 Revisando tu base de datos local...")
    print("========================================")

    db_path = "medizen_core.db"

    if not os.path.exists(db_path):
        print(f"❌ ERROR: No se encontró el archivo '{db_path}'.")
        print("¿Aseguraste de cambiarle el nombre al respaldo como te indiqué?")
        return

    size_kb = os.path.getsize(db_path) / 1024
    print(f"📄 Tamaño del archivo: {size_kb:.2f} KB")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Revisar pacientes
        cursor.execute("SELECT count(*) FROM patients")
        patients = cursor.fetchone()[0]
        if patients > 0:
            print(f"✅ EXCELENTE: ¡Se encontraron {patients} pacientes! Tus datos están a salvo.")
        else:
            print(f"⚠️ ADVERTENCIA: Hay 0 pacientes. Parece que esta base de datos sigue vacía.")

        # Revisar planes
        cursor.execute("SELECT count(*) FROM membership_plans")
        plans = cursor.fetchone()[0]
        if plans > 0:
            print(f"✅ EXCELENTE: Se encontraron {plans} planes de membresía. El portal web los mostrará.")
        else:
            print(f"⚠️ ADVERTENCIA: Hay 0 planes de membresía.")

        # Revisar actualización Alembic
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='booking_locks'")
        has_locks = cursor.fetchone()
        if has_locks:
            print("✅ EXCELENTE: La base de datos está actualizada con la nueva seguridad.")
        else:
            print("❌ FALTA ACTUALIZAR: La base de datos es antigua y no tiene los nuevos candados.")
            print("Debes ejecutar: .\\.venv\\Scripts\\python.exe -m alembic upgrade head")

    except Exception as e:
        print(f"❌ Error al intentar leer la base de datos: {e}")

    print("========================================")

if __name__ == "__main__":
    check()
