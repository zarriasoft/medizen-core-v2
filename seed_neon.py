"""
Script para crear el usuario admin en la base de datos Neon PostgreSQL.
"""
import subprocess, sys

# Instalar dependencias necesarias
subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary", "bcrypt", "--quiet"], capture_output=True)

import os
import psycopg2
import bcrypt

NEON_URL = os.environ.get("DATABASE_URL")
if not NEON_URL:
    print("ERROR: Debes configurar la variable de entorno DATABASE_URL")
    print("  Ejemplo: set DATABASE_URL=postgresql://usuario:password@host/dbname?sslmode=require")
    sys.exit(1)

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

conn = psycopg2.connect(NEON_URL)
cur = conn.cursor()
print("Conectado a Neon PostgreSQL...")

# Crear tabla users si no existe
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR UNIQUE NOT NULL,
        email VARCHAR UNIQUE NOT NULL,
        hashed_password VARCHAR NOT NULL,
        full_name VARCHAR,
        role VARCHAR DEFAULT 'staff',
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
""")
print("Tabla 'users' verificada/creada.")

# Verificar si ya existe admin
cur.execute("SELECT id FROM users WHERE username = 'admin'")
existing = cur.fetchone()

if existing:
    hashed = hash_password("adminpassword")
    cur.execute("UPDATE users SET hashed_password = %s WHERE username = 'admin'", (hashed,))
    print("Usuario admin ya existia -> contrasena actualizada.")
else:
    hashed = hash_password("adminpassword")
    cur.execute("""
        INSERT INTO users (username, email, hashed_password, full_name, role, is_active)
        VALUES ('admin', 'admin@medizen.com', %s, 'Administrador', 'admin', TRUE)
    """, (hashed,))
    print("Usuario admin creado exitosamente!")

conn.commit()
cur.close()
conn.close()

print("\n============================")
print("LISTO! Ingresa con:")
print("  Usuario:    admin")
print("  Contrasena: adminpassword")
print("============================")
