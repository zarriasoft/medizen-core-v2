import sqlite3
import json

db_path = 'C:/Medizen/v2/backend/medizen_core.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory
cur = conn.cursor()

cur.execute("SELECT * FROM patients WHERE last_name LIKE '%Zarria%' OR last_name LIKE '%Sarria%' OR first_name LIKE '%Zarria%' OR first_name LIKE '%Sarria%'")
patients = cur.fetchall()

print("PATIENTS_FOUND:")
print(json.dumps(patients, indent=2))

conn.close()
