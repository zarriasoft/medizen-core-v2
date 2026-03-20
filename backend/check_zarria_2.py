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

print("IEIM RECORDS FOR PATIENT 1:")
cur.execute("SELECT * FROM ieim_records WHERE patient_id = 1")
print(json.dumps(cur.fetchall(), indent=2))

print("\nMEMBERSHIPS FOR PATIENT 1:")
cur.execute("SELECT * FROM memberships WHERE patient_id = 1")
print(json.dumps(cur.fetchall(), indent=2))

conn.close()
