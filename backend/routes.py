# backend/routes.py
import os
from flask import Blueprint, request, jsonify
from models import db, Product, Image
from werkzeug.utils import secure_filename

# --- เพิ่มการตั้งค่าสำหรับ Upload ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

api_bp = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- แก้ไขฟังก์ชัน add_product ---
@api_bp.route('/products', methods=['POST'])
def add_product():
    # รับข้อมูลจากฟอร์ม (ไม่ใช่ JSON แล้ว)
    if 'product-name' not in request.form:
        return jsonify({'message': 'Missing product name'}), 400

    # สร้าง Product object ใหม่
    new_product = Product(
        name=request.form['product-name'],
        description=request.form.get('product-description'),
        price=float(request.form['product-price']),
        category=request.form['product-category'],
        status=request.form.get('status', 'available')
    )
    
    # จัดการไฟล์ที่อัปโหลด
    if 'product-images[]' in request.files:
        files = request.files.getlist('product-images[]')
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # สร้าง path ที่จะ save ไฟล์
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # ตรวจสอบและสร้างโฟลเดอร์ถ้ายังไม่มี
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                file.save(save_path)
                
                # สร้าง Image object ใหม่ และเชื่อมกับ Product
                new_image = Image(url=save_path, product=new_product)
                db.session.add(new_image)

    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully!', 'product': new_product.to_json()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create product', 'error': str(e)}), 500

# ... (ฟังก์ชัน get_products ไม่ต้องแก้ไข) ...
@api_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_json() for p in products])
