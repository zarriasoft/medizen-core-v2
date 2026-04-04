import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
sys.path.append('C:/Medizen/v2/backend')
from app.models import SystemSettings
engine = create_engine('sqlite:///C:/Medizen/v2/backend/medizen_core.db')
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
s = db.query(SystemSettings).first()
if s:
    print(f'HOST: {s.smtp_host}, PORT: {s.smtp_port}, USER: {s.smtp_user}, ADMIN: {s.admin_email}')
    print(f'PASS LENGTH: {len(s.smtp_password) if s.smtp_password else 0}')
else:
    print('No settings found in DB')
