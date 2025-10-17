# Flask CRUD API with Authentication (Django-Style Structure)

A complete Flask REST API with CRUD operations, JWT authentication, role-based access control, and image upload functionality, organized using Django's folder structure pattern.

## Project Structure

```
project/
├── manage.py                    # Django-style management script
├── uploads/                     # Local storage for uploaded images
│   └── products/                   # Product images
├── project/
│   ├── __init__.py             # Application factory
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Configuration settings
│   │   └── extensions.py       # Flask extensions
│   └── apps/
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── models.py       # User model with roles
│       │   ├── views.py        # Route handlers
│       │   ├── validators.py        # Validators
│       │   ├── decorators.py   # Role-based decorators
│       │   └── urls.py         # URL patterns
│       └── products/
│           ├── __init__.py
│           ├── models.py       # Product model with image support
│           ├── views.py        # Route handlers
│           ├── validators.py        # Validators
│           └── urls.py         # URL patterns
```

## Features

- ✅ User registration and login with JWT authentication
- ✅ Role-based access control (Buyer, Seller, Admin)
- ✅ Password hashing with bcrypt
- ✅ CRUD operations for products with role-based permissions
- ✅ Image upload and storage for products
- ✅ Input validation for all endpoints
- ✅ SQLAlchemy ORM with SQLite database
- ✅ Protected routes with JWT tokens
- ✅ Pagination support for listing products
- ✅ Error handling
- ✅ Django-style project organization
- ✅ Application factory pattern

## User Roles

### Buyer

- Can view all products
- Cannot create, update, or delete products
- Default role for new users

### Seller

- Can create products
- Can view and manage their own products
- Can upload images for their products
- Cannot view other sellers' products

### Admin

- Full access to all products
- Can create, update, and delete any product
- Can view all products from all sellers

## Setup

1. Install dependencies:

```bash
pipenv shell
pipenv install
```

2. Set environment variables:

```bash
cp .env.example .env
```

And edit your .env file

3. Initialize the database:

```bash
pipenv run python3 main.py init-db
```

4. Run the application:

```bash
pipenv run python3 main.py run
```

Or use Flask's built-in server:

```bash
flask run
```

The API will be available at `http://localhost:5000`

## Management Commands

The `main.py` script provides Django-style management commands:

- `pipenv run python3 main.py init-db` - Initialize the database
- `pipenv run python3 main.py drop-db` - Drop all database tables
- `pipenv run python3 main.py run` - Run the development server

## API Endpoints

### Authentication

**Register a new user**

```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "buyer"  # Optional: "buyer", "seller" (default: "buyer")
}
```

**Login**

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

**Logout** (requires authentication)

```bash
POST /api/auth/logout
Authorization: Bearer <your_jwt_token>
```

**Get user profile** (requires authentication)

```bash
GET /api/auth/profile
Authorization: Bearer <your_jwt_token>
```

### Products

**Create a product** (requires Seller or Admin role)

Using JSON:

```bash
POST /api/products
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Laptop",
  "description": "Dell XPS 15",
  "quantity": 5,
  "price": 1299.99
}
```

Using form-data (for image upload):

```bash
POST /api/products
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data

# Form data:
title: "Laptop"
description: "Dell XPS 15"
quantity: 5
price: 1299.99
image: <file>  # Optional image file
```

**Get all products** (requires authentication)

```bash
GET /api/products?page=1&per_page=10
Authorization: Bearer <your_jwt_token>

# Buyers and Admins see all products
# Sellers see only their own products
```

**Get a specific product** (requires authentication)

```bash
GET /api/products/1
Authorization: Bearer <your_jwt_token>
```

**Update a product** (requires Seller or Admin role)

```bash
PUT /api/products/1
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data

# Form data:
title: "Updated Laptop"
quantity: 3
price: 1199.99
image: <file>  # Optional new image file

# Sellers can only update their own products
# Admins can update any product
```

**Delete a product** (requires Seller or Admin role)

```bash
DELETE /api/products/1
Authorization: Bearer <your_jwt_token>

# Sellers can only delete their own products
# Admins can delete any product
```

**Get product image**

```bash
GET /api/products/images/<filename>
```

## Validation Rules

### User Registration

- Username: 3-80 characters, required, unique
- Email: Valid email format, required, unique
- Password: Minimum 6 characters, required
- Role: Optional, must be "buyer", "seller", or "admin" (default: "buyer")

### Products

- Title: 1-100 characters, required
- Description: Optional text
- Quantity: Non-negative integer, optional (default: 0)
- Price: Non-negative number, optional (default: 0.0)
- Image: Optional, must be png, jpg, jpeg, gif, or webp (max 16MB)

## Database

The application uses SQLite by default. The database file `app.db` will be created automatically when you initialize the database.

### Database Schema

**Users Table:**

- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- role (buyer/seller/admin)
- created_at

**Products Table:**

- id (Primary Key)
- title
- description
- quantity
- price
- image_path (path to uploaded image)
- user_id (Foreign Key to Users)
- created_at
- updated_at

## File Storage

Product images are stored locally in the `uploads/products/` directory. Each image is saved with a secure filename format: `product_{id}_{random_hash}.{extension}`

## Security

- Passwords are hashed using bcrypt
- JWT tokens expire after 1 hour
- Protected routes require valid JWT token
- Role-based access control for sensitive operations
- File upload validation (type and size)
- Secure filename generation for uploads

## Architecture

This project follows Django's organizational patterns:

- **Application Factory**: The app is created using the factory pattern in `project/__init__.py`
- **Apps Structure**: Each feature (auth, products) is organized as a separate app with its own models, views, validators, and URLs
- **Configuration**: Settings are centralized in `project/config/settings.py`
- **Extensions**: Flask extensions are initialized in `project/config/extensions.py`
- **Management Commands**: Django-style CLI commands via `manage.py`
- **Role-Based Access Control**: Decorators for protecting routes based on user roles
