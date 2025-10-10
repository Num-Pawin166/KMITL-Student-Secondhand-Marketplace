# backend/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ... (คลาส User ไม่ต้องแก้ไข) ...

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # เพิ่มความสัมพันธ์: บอกว่า Product 1 ชิ้น มี Images ได้หลายอัน
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
            # เพิ่ม: ส่ง URL ของรูปภาพทั้งหมดไปด้วย
            'image_urls': [image.url for image in self.images]
        }

# --- สร้างคลาส Image ใหม่ ---
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # เราจะเก็บแค่ URL หรือ path ของไฟล์รูป
    url = db.Column(db.String(255), nullable=False)
    
    # สร้าง Foreign Key เพื่อเชื่อมกลับไปที่ตาราง Product
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)