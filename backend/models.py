# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # <-- Import UserMixin

db = SQLAlchemy()

# --- ▼▼▼ เพิ่มคลาส User ใหม่ และแก้ไขให้รองรับ Flask-Login ▼▼▼ ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # เราจะเก็บแค่ hash ของรหัสผ่าน ไม่เก็บรหัสผ่านตรงๆ
    password_hash = db.Column(db.String(128), nullable=False)
    
    # ความสัมพันธ์: บอกว่า User 1 คน มี Product ได้หลายชิ้น
    products = db.relationship('Product', backref='owner', lazy=True)


# --- ▼▼▼ แก้ไขคลาส Product เพื่อเชื่อมกับ User ▼▼▼ ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # เพิ่ม Foreign Key เพื่อชี้ไปที่เจ้าของสินค้า
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    images = db.relationship('Image', backref='product', lazy=True, cascade="all, delete-orphan")

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'image_urls': [image.url for image in self.images],
            # เพิ่ม: ส่ง username ของเจ้าของสินค้าไปด้วย
            'owner_username': self.owner.username 
        }

# --- คลาส Image (ไม่ต้องแก้ไข) ---
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)