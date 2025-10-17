"""Products URL patterns (routes)"""

from flask import Blueprint
from project.apps.products import views

products_bp = Blueprint("products", __name__)

# Register routes
products_bp.add_url_rule("", "create_product", views.create_product, methods=["POST"])
products_bp.add_url_rule("", "get_products", views.get_products, methods=["GET"])
products_bp.add_url_rule(
    "/<int:product_id>", "get_product", views.get_product, methods=["GET"]
)
products_bp.add_url_rule(
    "/<int:product_id>", "update_product", views.update_product, methods=["PUT"]
)
products_bp.add_url_rule(
    "/<int:product_id>", "delete_product", views.delete_product, methods=["DELETE"]
)
products_bp.add_url_rule(
    "/upload-image", "upload_image", views.upload_image, methods=["POST"]
)
products_bp.add_url_rule(
    "/images/<path:filename>", "serve_image", views.serve_image, methods=["GET"]
)
