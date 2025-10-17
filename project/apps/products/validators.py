"""Product form validators"""


def validate_product(data, is_update=False):
    """Validate product data"""
    errors = []

    # For creation, title is required. For updates, it's optional
    if not is_update:
        if not data.get("title"):
            errors.append("Title is required")
        elif len(data["title"]) < 1:
            errors.append("Title cannot be empty")
        elif len(data["title"]) > 100:
            errors.append("Title must be less than 100 characters")
    else:
        if "title" in data:
            if not data["title"] or len(data["title"]) < 1:
                errors.append("Title cannot be empty")
            elif len(data["title"]) > 100:
                errors.append("Title must be less than 100 characters")

    # Validate quantity if provided
    if "quantity" in data:
        try:
            quantity = int(data["quantity"])
            if quantity < 0:
                errors.append("Quantity cannot be negative")
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid integer")

    # Validate price if provided
    if "price" in data:
        try:
            price = float(data["price"])
            if price < 0:
                errors.append("Price cannot be negative")
        except (ValueError, TypeError):
            errors.append("Price must be a valid number")

    return len(errors) == 0, errors
