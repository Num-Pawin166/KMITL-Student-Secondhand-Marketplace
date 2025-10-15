# backend/app.py
import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user
from sqlalchemy.orm.exc import NoResultFound

from extensions import db, bcrypt, login_manager
from routes import api_bp # <--- import blueprint
from models import User
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app, supports_credentials=True)

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# (ส่วนของ Google Login ไม่ต้องแก้ไข)
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
        return redirect("http://127.0.0.1:5500/User-Login.html")

    user_info = google.get("/oauth2/v2/userinfo").json()
    user_email = user_info["email"]
    user_name = user_info.get("name", user_email.split('@')[0])
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        user = User(username=user_name, email=user_email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect("http://127.0.0.1:5500/index.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ▼▼▼ จุดที่แก้ไข ▼▼▼ ---
# ลงทะเบียน API routes และกำหนด prefix ให้ทุก route ในนั้นขึ้นต้นด้วย /api
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, port=5000)