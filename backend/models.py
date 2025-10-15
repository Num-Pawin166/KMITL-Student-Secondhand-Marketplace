# backend/models.py
from extensions import db # <-- แก้ไข: import db จาก extensions
from flask_login import UserMixin

# --- แก้ไขคลาส User ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # username อาจซ้ำกันได้ถ้ามาจากชื่อ Google Account
    username = db.Column(db.String(80), unique=False, nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password_hash สามารถเป็น NULL ได้ สำหรับคนที่ login ด้วย Google
    password_hash = db.Column(db.String(128), nullable=True) 
    
    products = db.relationship('Product', backref='owner', lazy=True)

# --- แก้ไขคลาส Product ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
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
            'owner_username': self.owner.username,
            'owner_id': self.owner_id 
        }
# --- คลาส Image (ไม่ต้องแก้ไข) ---
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)