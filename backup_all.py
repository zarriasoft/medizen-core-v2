#!/usr/bin/env python
"""
MediZen v2 - Script de respaldo unificado.
Uso:
  python backup.py              # Respaldo completo (DB local + cloud + app)
  python backup.py --db         # Solo base de datos local
  python backup.py --cloud      # Solo base de datos cloud (Neon)
  python backup.py --files      # Solo archivos de la app
  python backup.py --full       # Respaldo completo (igual que sin args)
"""
import os
import sys
import zipfile
import shutil
import json
from datetime import datetime
from sqlalchemy import create_engine, text

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = SCRIPT_DIR

BACKUP_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), f"backups_{TIMESTAMP}")
os.makedirs(BACKUP_DIR, exist_ok=True)

APP_ZIP = os.path.join(BACKUP_DIR, "medizen_v2_app.zip")
LOCAL_DB_BACKUP = os.path.join(BACKUP_DIR, "medizen_core_local.db")
CLOUD_DB_BACKUP = os.path.join(BACKUP_DIR, "medizen_neon_cloud.json")


def backup_local_db():
    local_db_path = os.path.join(SOURCE_DIR, "backend", "medizen_core.db")
    if os.path.exists(local_db_path):
        shutil.copy2(local_db_path, LOCAL_DB_BACKUP)
        print(f"[OK] Local DB respaldada en: {LOCAL_DB_BACKUP}")
    else:
        print("[WARN] Local DB no encontrada.")


def backup_cloud_db():
    NEON_URL = os.environ.get("DATABASE_URL")
    if not NEON_URL:
        print("[WARN] Cloud DB backup omitido: DATABASE_URL no configurada.")
        return
    try:
        engine = create_engine(NEON_URL)
        tables = [
            "users", "patients", "membership_plans", "programs",
            "memberships", "appointments", "ieim_records",
            "clinical_histories", "system_settings",
            "specialist_schedules", "schedule_overrides", "payments"
        ]
        backup_data = {}
        with engine.connect() as conn:
            for table in tables:
                rows = conn.execute(text(f"SELECT * FROM {table}")).mappings().all()
                backup_data[table] = [dict(r) for r in rows]
                for row in backup_data[table]:
                    for k, v in row.items():
                        if hasattr(v, 'isoformat'):
                            row[k] = v.isoformat()
        with open(CLOUD_DB_BACKUP, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"[OK] Cloud DB respaldada en: {CLOUD_DB_BACKUP}")
    except Exception as e:
        print(f"[ERROR] Error al respaldar Cloud DB: {e}")


def backup_files():
    exclude_dirs = {'node_modules', '.venv', '__pycache__', '.git', 'dist', 'build'}
    print("Empaquetando aplicacion...")
    with zipfile.ZipFile(APP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                if not file.endswith('.zip'):
                    arcname = os.path.relpath(file_path, SOURCE_DIR)
                    zipf.write(file_path, arcname)
    print(f"[OK] Aplicacion respaldada en: {APP_ZIP}")


if __name__ == "__main__":
    args = set(sys.argv[1:])
    do_all = not args or "--full" in args
    print("--- INICIANDO RESPALDO MEDIZEN v2 ---")
    if do_all or "--db" in args:
        backup_local_db()
    if do_all or "--cloud" in args:
        backup_cloud_db()
    if do_all or "--files" in args:
        backup_files()
    print(f"RESPALDO COMPLETO EN: {BACKUP_DIR}")
