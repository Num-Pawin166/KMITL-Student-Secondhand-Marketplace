# backend/app.py
import os
from flask import Flask, redirect, url_for, send_from_directory
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user
from sqlalchemy.orm.exc import NoResultFound
from flask_socketio import SocketIO, join_room, leave_room, send
from werkzeug.middleware.proxy_fix import ProxyFix # <-- 1. เพิ่ม import นี้

# ▼▼▼ แก้ไขการ import ทั้งหมดที่นี่ ▼▼▼
# ลบ 'backend.' ออก เพื่อให้ทำงานบน Render ได้ถูกต้อง
from config import Config
from extensions import db, bcrypt, login_manager
from routes import api_bp
from models import User
from flask_cors import CORS

# --- การตั้งค่า App ---
frontend_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
app = Flask(__name__, static_folder=frontend_folder)
app.config.from_object(Config)

# --- ▼▼▼ 2. เพิ่ม Middleware 'ProxyFix' ▼▼▼ ---
# โค้ดบรรทัดนี้ทำหน้าที่เหมือน 'ล่าม' ที่จะบอกแอป Flask ของเราว่า
# "เฮ้! ให้เชื่อใจ header ที่ proxy (ของ Render) ส่งมาด้วยนะ"
# ซึ่งจะทำให้ Flask รู้ว่าผู้ใช้กำลังเข้าเว็บผ่าน https
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# --- ส่วนที่เหลือ (เหมือนเดิม) ---
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app, supports_credentials=True)
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

google_bp = make_google_blueprint(
    client_id=app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="post_login",
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/post-google-login")
def post_login():
    if not google.authorized:
        return redirect(url_for('serve_index'))

    user_info = google.get("/oauth2/v2/userinfo").json()
    user_email = user_info["email"]
    user_name = user_info.get("name", user_email.split('@')[0])
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        user = User(username=user_name, email=user_email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('serve_index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(api_bp, url_prefix='/api')

# --- Logic การแชท ---
@socketio.on('join')
def on_join(data):
    username = data.get('username', 'Anonymous')
    room = data.get('room')
    if room:
        join_room(room)
        print(f'{username} has entered the room: {room}')

@socketio.on('send_message')
def handle_send_message(data):
    room = data.get('room')
    if room:
        socketio.emit('receive_message', data, to=room)
        print(f"Message in room {room} from {data.get('username')}: {data.get('message')}")
    
# --- ส่วนของการเสิร์ฟหน้าเว็บ ---
@app.route('/')
def serve_index():
    return send_from_directory(frontend_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(frontend_folder, path)):
        return send_from_directory(frontend_folder, path)
    else:
        return send_from_directory(frontend_folder, 'index.html')

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    socketio.run(app, debug=True, port=5000)