"""Products views (route handlers)"""

from flask import request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from project.config.extensions import db
from project.apps.products.models import Product
from project.apps.products.validators import validate_product
from project.apps.auth.models import User, UserRole
from project.apps.auth.decorators import seller_required, admin_required

UPLOAD_FOLDER = "uploads/products"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_product_image(file, product_id):
    """Save product image to local storage"""
    if file and allowed_file(file.filename):
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Generate secure filename
        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        new_filename = f"product_{product_id}_{os.urandom(8).hex()}.{ext}"

        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(filepath)

        return filepath
    return None


@jwt_required()
@seller_required
def upload_image():
    """Upload an image and return the path (sellers and admins only)"""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "No image file selected"}), 400

    if not allowed_file(image_file.filename):
        return (
            jsonify(
                {
                    "error": f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
                }
            ),
            400,
        )

    try:
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Generate secure filename
        filename = secure_filename(image_file.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        new_filename = f"temp_{os.urandom(16).hex()}.{ext}"

        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        image_file.save(filepath)

        return (
            jsonify({"message": "Image uploaded successfully", "image_path": filepath}),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500


@jwt_required()
@seller_required
def create_product():
    """Create a new product (sellers and admins only)"""
    current_user_id = get_jwt_identity()

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get("image")
    else:
        data = request.get_json()
        image_file = None

    # Validate input
    is_valid, errors = validate_product(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400

    # Create new product
    new_product = Product(
        title=data["title"],
        description=data.get("description", ""),
        quantity=int(data.get("quantity", 0)),
        price=float(data.get("price", 0.0)),
        user_id=current_user_id,
    )

    try:
        db.session.add(new_product)
        db.session.flush()  # Get product ID before commit

        if image_file:
            image_path = save_product_image(image_file, new_product.id)
            if image_path:
                new_product.image_path = image_path

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Product created successfully",
                    "product": new_product.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create product: {str(e)}"}), 500


@jwt_required()
def get_products():
    """Get all products (buyers see all, sellers see their own)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    # Get query parameters for pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if user.role == UserRole.BUYER or user.role == UserRole.ADMIN:
        products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    else:
        products = Product.query.filter_by(user_id=current_user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )

    return (
        jsonify(
            {
                "products": [product.to_dict() for product in products.products],
                "total": products.total,
                "page": products.page,
                "pages": products.pages,
            }
        ),
        200,
    )


@jwt_required()
def get_product(product_id):
    """Get a single product"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user.role == UserRole.BUYER or user.role == UserRole.ADMIN:
        product = Product.query.get(product_id)
    else:
        product = Product.query.filter_by(
            id=product_id, user_id=current_user_id
        ).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"product": product.to_dict()}), 200


@jwt_required()
@seller_required
def update_product(product_id):
    """Update a product (sellers can update their own, admins can update any)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user.role == UserRole.ADMIN:
        product = Product.query.get(product_id)
    else:
        product = Product.query.filter_by(
            id=product_id, user_id=current_user_id
        ).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get("image")
    else:
        data = request.get_json()
        image_file = None

    # Validate input
    is_valid, errors = validate_product(data, is_update=True)
    if not is_valid:
        return jsonify({"errors": errors}), 400

    # Update product fields
    if "title" in data:
        product.title = data["title"]
    if "description" in data:
        product.description = data["description"]
    if "quantity" in data:
        product.quantity = int(data["quantity"])
    if "price" in data:
        product.price = float(data["price"])

    if image_file:
        # Delete old image if exists
        if product.image_path and os.path.exists(product.image_path):
            os.remove(product.image_path)

        image_path = save_product_image(image_file, product.id)
        if image_path:
            product.image_path = image_path

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Product updated successfully",
                    "product": product.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update product: {str(e)}"}), 500


@jwt_required()
@seller_required
def delete_product(product_id):
    """Delete a product (sellers can delete their own, admins can delete any)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user.role == UserRole.ADMIN:
        product = Product.query.get(product_id)
    else:
        product = Product.query.filter_by(
            id=product_id, user_id=current_user_id
        ).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        if product.image_path and os.path.exists(product.image_path):
            os.remove(product.image_path)

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete product: {str(e)}"}), 500


def serve_image(filename):
    """Serve product images from local storage"""
    return send_from_directory(UPLOAD_FOLDER, filename)
