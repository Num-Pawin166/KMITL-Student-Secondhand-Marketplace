# backend/app.py
import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user, current_user
from sqlalchemy.orm.exc import NoResultFound

from extensions import db, bcrypt, login_manager
from routes import api_bp
from models import User
from flask_cors import CORS

# สร้าง Flask App
app = Flask(__name__)
# โหลดการตั้งค่าทั้งหมดจากไฟล์ config.py
app.config.from_object('config.Config')

# ▼▼▼ เพิ่ม 2 บรรทัดนี้เพื่อ DEBUG ▼▼▼
print(f"--- Loaded Client ID: {app.config.get('GOOGLE_OAUTH_CLIENT_ID')}")
print(f"--- Loaded Client Secret: {app.config.get('GOOGLE_OAUTH_CLIENT_SECRET')}")
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

# ตั้งค่า CORS ให้รองรับการส่ง credentials (session cookie)
CORS(app, supports_credentials=True)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# --- ส่วนของ Flask-Dance สำหรับ Google Login ---

google_bp = make_google_blueprint(
    client_id=app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    # หลังจาก Google อนุญาต จะให้ redirect มาที่ route นี้
    redirect_to="post_login",
)

# ลงทะเบียน blueprint นี้กับ app หลัก
app.register_blueprint(google_bp, url_prefix="/login")

# --- Logic หลังจาก Login ผ่าน Google สำเร็จ ---

@app.route("/post-google-login")
def post_login():
    if not google.authorized:
        # ถ้าไม่ได้รับอนุญาต, กลับไปหน้า login ของ frontend
        return redirect("http://127.0.0.1:5500/User-Login.html")

    # ดึงข้อมูล user จาก Google
    user_info = google.get("/oauth2/v2/userinfo").json()
    user_email = user_info["email"]
    user_name = user_info.get("name", user_email.split('@')[0])

    # ค้นหา user ใน DB จาก email ที่ได้มา
    user = User.query.filter_by(email=user_email).first()

    if not user:
        # ถ้า user ยังไม่มีในระบบ, สร้างใหม่
        user = User(
            username=user_name,
            email=user_email,
        )
        db.session.add(user)
        db.session.commit()

    # ล็อกอิน user เข้าสู่ระบบด้วย Flask-Login
    login_user(user)
    
    # **สำคัญ:** Redirect ไปยังหน้า Frontend หลักของคุณ (อาจจะเป็น index.html)
    # แก้ไข URL นี้ให้ถูกต้องตามโปรเจกต์ของคุณ
    return redirect("http://127.0.0.1:5500/index.html")

# --- User Loader ของ Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ลงทะเบียน API routes เดิม ---
app.register_blueprint(api_bp)


if __name__ == "__main__":
    # **สำคัญ:** บรรทัดนี้จำเป็นสำหรับการทดสอบบน Local (HTTP) เท่านั้น
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, port=5000)