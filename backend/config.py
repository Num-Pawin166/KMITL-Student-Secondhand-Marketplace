# backend/config.py
import os

class Config:
    # ตั้งค่าการเชื่อมต่อ PostgreSQL โดยใช้ข้อมูลที่คุณให้มา
    # user = postgres
    # password = 1234
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:1234@localhost:5432/marketplace_db'
    
    # ไม่ต้องแก้ไขส่วนนี้
    SQLALCHEMY_TRACK_MODIFICATIONS = False