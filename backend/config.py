# backend/config.py
import os

class Config:
    # ตั้งค่าการเชื่อมต่อ PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:1234@localhost:5432/marketplace_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- การตั้งค่าสำหรับ Google OAuth ---
    # Flask-Dance ต้องการ Secret Key สำหรับการสร้าง session
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-for-dev'
    
    # ดึงค่า Client ID และ Secret จาก Environment Variables เพื่อความปลอดภัย
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')