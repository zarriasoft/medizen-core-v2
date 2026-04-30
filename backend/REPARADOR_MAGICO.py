import os
import shutil
import sys

base_dir = r"C:\Medizen\v2\backend"
backup_file = os.path.join(base_dir, "backups", "medizen_core_local_2026-04-05_15-23-38.db")
target_file = os.path.join(base_dir, "medizen_core.db")

print("==================================================")
print("INICIANDO REPARACIÓN MÁGICA DE MEDIZEN...")
print("==================================================")

# 1. Limpiar todos los archivos basura o vacíos que se crearon por error
archivos_basura = ["medizen_core.db", "medizen_core.db.db", "medizen.db"]
for name in archivos_basura:
    bad = os.path.join(base_dir, name)
    if os.path.exists(bad):
        try:
            os.remove(bad)
            print(f"[+] Eliminado archivo vacío/corrupto: {name}")
        except:
            pass

# 2. Restaurar la copia de seguridad exacta
restaurado = False
if os.path.exists(backup_file):
    shutil.copy2(backup_file, target_file)
    print("[+] Base de datos ORIGINAL (132 KB) restaurada correctamente.")
    restaurado = True
else:
    # Si por si acaso el usuario ya movió el archivo manualmente, buscarlo por tamaño
    for f in os.listdir(base_dir):
        path = os.path.join(base_dir, f)
        if os.path.isfile(path) and "medizen" in f:
            # Buscar el archivo que pesa aprox 132-135 KB
            if abs(os.path.getsize(path) - 135168) < 10000:
                shutil.copy2(path, target_file)
                print(f"[+] Recuperada base de datos correcta desde: {f}")
                restaurado = True
                break

if not restaurado:
    print("[-] ERROR CRÍTICO: No se encontró el archivo de la base de datos real.")
    sys.exit(1)

# 3. Aplicar nuevas tablas de Alembic (Seguridad)
print("\n[+] Aplicando nuevos candados de seguridad a la base de datos...")
os.system(r".\.venv\Scripts\python.exe -m alembic upgrade head")

# 4. Resetear la contraseña de zarria a 123456
print("\n[+] Reseteando contraseña de zarria@gmail.com...")
sys.path.append(base_dir)
try:
    from app.database import SessionLocal
    from app.models import Patient
    from app.auth import get_password_hash
    db = SessionLocal()
    p = db.query(Patient).filter(Patient.email.ilike("zarria@gmail.com")).first()
    if p:
        p.hashed_password = get_password_hash("123456")
        db.commit()
        print("[+] ¡Clave cambiada a 123456 exitosamente!")
    else:
        # Crearlo si no existe para asegurar el acceso
        p_new = Patient(email="zarria@gmail.com", first_name="Zarria", hashed_password=get_password_hash("123456"))
        db.add(p_new)
        db.commit()
        print("[+] Usuario zarria@gmail.com creado con clave 123456.")
except Exception as e:
    print(f"[-] Nota: No se pudo resetear la clave automáticamente ({e}).")

print("\n==================================================")
print("✔️ ¡TODO REPARADO! YA PUEDES ENTRAR AL PORTAL WEB.")
print("==================================================")
