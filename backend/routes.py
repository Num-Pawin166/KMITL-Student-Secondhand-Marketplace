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
    # เพิ่ม .order_by(Product.created_at.desc()) เพื่อเรียงตามวันที่สร้างล่าสุด
    products = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify([p.to_json() for p in products])

# --- ▼▼▼ เพิ่มฟังก์ชันใหม่นี้เข้าไปต่อท้ายไฟล์ ▼▼▼ ---
@api_bp.route('/products/category/<string:category_name>', methods=['GET'])
def get_products_by_category(category_name):
    """
    API endpoint เพื่อดึงสินค้าทั้งหมดในหมวดหมู่ที่ระบุ
    """
    try:
        # แปลงชื่อหมวดหมู่ที่อาจจะส่งมาจาก frontend ให้ตรงกับที่เก็บใน DB
        # เช่น 'appliances' -> 'appliances', 'clothing' -> 'clothing'
        
        # ค้นหาสินค้าทั้งหมดที่ตรงกับ category_name
        products = Product.query.filter_by(category=category_name).all()
        
        # ส่งข้อมูลกลับไปเป็น JSON
        return jsonify([p.to_json() for p in products])
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to fetch products by category', 'error': str(e)}), 500

# --- ▼▼▼ เพิ่ม 2 ฟังก์ชันใหม่นี้เข้าไป ▼▼▼ ---

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_single_product(product_id):
    """ API endpoint เพื่อดึงข้อมูลสินค้าชิ้นเดียวตาม ID """
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_json())
    except Exception as e:
        return jsonify({'message': 'Product not found', 'error': str(e)}), 404

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """ API endpoint สำหรับอัปเดตข้อมูลสินค้า """
    try:
        product_to_update = Product.query.get_or_404(product_id)
        
        # อัปเดตข้อมูลจากฟอร์มที่ส่งมา
        product_to_update.name = request.form['product-name']
        product_to_update.description = request.form.get('product-description')
        product_to_update.price = float(request.form['product-price'])
        product_to_update.category = request.form['product-category']
        product_to_update.status = request.form.get('status', 'available')

        # (Optional) ในอนาคตอาจจะเพิ่ม logic การลบ/เพิ่มรูปภาพใหม่ที่นี่
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully!', 'product': product_to_update.to_json()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 500


