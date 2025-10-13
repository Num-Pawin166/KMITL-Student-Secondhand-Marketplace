# backend/routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from extensions import db, bcrypt
from models import User, Product, Image
# --- เพิ่มการตั้งค่าสำหรับ Upload ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

api_bp = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ฟังก์ชันสำหรับสินค้า (ป้องกันด้วย @login_required) ---
@api_bp.route('/products', methods=['POST'])
@login_required # <-- ป้องกัน: ต้อง login ก่อนถึงจะเพิ่มสินค้าได้
def add_product():
    if 'product-name' not in request.form:
        return jsonify({'message': 'Missing product name'}), 400

    # สร้าง Product object ใหม่ โดยระบุ owner เป็น user ที่ login อยู่
    new_product = Product(
        name=request.form['product-name'],
        description=request.form.get('product-description'),
        price=float(request.form['product-price']),
        category=request.form['product-category'],
        status=request.form.get('status', 'available'),
        owner_id=current_user.id # <-- เชื่อมสินค้ากับเจ้าของ
    )
    
    if 'product-images[]' in request.files:
        files = request.files.getlist('product-images[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(save_path)
                new_image = Image(url=save_path, product=new_product)
                db.session.add(new_image)

    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully!', 'product': new_product.to_json()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create product', 'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@login_required # <-- ป้องกัน: ต้อง login ก่อนถึงจะแก้ไขสินค้าได้
def update_product(product_id):
    try:
        product_to_update = Product.query.get_or_404(product_id)
        
        # (แนะนำ) เพิ่มการตรวจสอบว่าเป็นเจ้าของสินค้าจริงหรือไม่
        if product_to_update.owner_id != current_user.id:
            return jsonify({'message': 'Unauthorized to edit this product'}), 403

        product_to_update.name = request.form['product-name']
        product_to_update.description = request.form.get('product-description')
        product_to_update.price = float(request.form['product-price'])
        product_to_update.category = request.form['product-category']
        product_to_update.status = request.form.get('status', 'available')
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully!', 'product': product_to_update.to_json()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 500

# --- API สำหรับดึงข้อมูลสินค้า (ไม่ต้อง login ก็ดูได้) ---
@api_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify([p.to_json() for p in products])

@api_bp.route('/products/category/<string:category_name>', methods=['GET'])
def get_products_by_category(category_name):
    try:
        products = Product.query.filter_by(category=category_name).all()
        return jsonify([p.to_json() for p in products])
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to fetch products by category', 'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_single_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_json())
    except Exception as e:
        return jsonify({'message': 'Product not found', 'error': str(e)}), 404

# --- API สำหรับระบบสมาชิก ---
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Username or email already exists'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
        
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user) # สร้าง session cookie
        return jsonify({'message': 'Login successful', 'user': {'username': user.username}})
    
    return jsonify({'message': 'Invalid username or password'}), 401

@api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user() # ลบ session cookie
    return jsonify({'message': 'Logout successful'})

@api_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """API ที่ frontend ใช้ถามว่า 'คนนี้ login หรือยัง?'"""
    if current_user.is_authenticated:
        return jsonify({'is_authenticated': True, 'user': {'username': current_user.username}})
    else:
        return jsonify({'is_authenticated': False}), 401

