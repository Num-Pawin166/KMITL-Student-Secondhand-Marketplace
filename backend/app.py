# backend/app.py
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import api_bp # import Blueprint จาก routes

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# เปิดใช้งาน CORS
CORS(app)

# เชื่อม SQLAlchemy กับ app
db.init_app(app)

# ลงทะเบียน Blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# สร้างตารางใน Database (ถ้ายังไม่มี)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)