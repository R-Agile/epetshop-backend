# PawStore Backend API - Complete Guide

## 🚀 Features Overview

### User Management
- **Registration & Login** - JWT-based authentication
- **Role-Based Access** - Admin vs Regular User
- **User Profiles** - Full name, email, password management

### Pet Management
- **Pet Types** - Dogs, Cats, Birds, Fishes (system managed)
- **User Pet Profiles** - Users can create and manage their own pets
  - Pet Name, Breed, Age, Type, Image, Notes
  - Edit/Delete functionality

### Shopping Features
- **Product Catalog** - Browse pets supplies and food
- **Categories & Subcategories** - Organized by pet type and product type
- **Inventory Management** - Stock tracking, pricing, discounts, visibility
- **Wishlist** - Save favorite items
- **Shopping Cart** - Add/remove items, update quantities

### Checkout & Orders
- **Multi-step Checkout** - Shipping → Payment → Review
- **Shipping Information** - First Name, Last Name, Email, Address, City, ZIP
- **Cash on Delivery** - Payment method (COD)
- **Order Tracking** - Status updates (pending, in_progress, dispatched, delivered, cancelled)

### Admin Dashboard
- **Dashboard Statistics** - Revenue, orders, users, low stock alerts
- **Inventory Management** - Add/Edit/Delete products, manage stock
- **Order Management** - View all orders, update status
- **User Management** - View all users, track their activity
- **Low Stock Alerts** - Monitor inventory levels

### Admin Credentials
```
Username: admin@epet.com
Password: admin1234
```

---

## 📚 API Endpoints

### Authentication
```
POST /users/register
- Register new user
- Body: { username, email, full_name, password, role }

POST /users/login
- Login user
- Body: { username, password } (form-data)

GET /users/me
- Get current logged-in user info
- Auth: Required (Bearer token)
```

### User Management (Admin Only)
```
GET /users/
- Get all users
- Auth: Admin required

GET /users/{user_id}
- Get specific user
- Auth: Required

PUT /users/{user_id}
- Update user
- Auth: Required

DELETE /users/{user_id}
- Delete user
- Auth: Admin required
```

### Pet Types (System)
```
GET /pets/
- Get all pet types

GET /pets/{pet_id}
- Get specific pet type

POST /pets/
- Create pet type
- Auth: Admin required

PUT /pets/{pet_id}
- Update pet type
- Auth: Admin required

DELETE /pets/{pet_id}
- Delete pet type
- Auth: Admin required
```

### User Pet Profiles (My Pets)
```
POST /pet-profiles/
- Create a new pet profile
- Auth: Required
- Body: {
    pet_name,
    pet_type_id,
    breed,
    age,
    image_url (optional),
    notes (optional)
  }

GET /pet-profiles/
- Get all my pet profiles
- Auth: Required

GET /pet-profiles/{pet_profile_id}
- Get specific pet profile
- Auth: Required

PUT /pet-profiles/{pet_profile_id}
- Update pet profile
- Auth: Required

DELETE /pet-profiles/{pet_profile_id}
- Delete pet profile
- Auth: Required
```

### Categories
```
GET /categories/
- Get all categories (Dogs, Cats, Birds, Fishes)

GET /categories/{category_id}
- Get specific category

POST /categories/
- Create category
- Auth: Admin required

PUT /categories/{category_id}
- Update category
- Auth: Admin required

DELETE /categories/{category_id}
- Delete category
- Auth: Admin required
```

### Subcategories
```
GET /subcategories/
- Get all subcategories (Accessories, Toys, Food, etc.)

GET /subcategories/{subcategory_id}
- Get specific subcategory

GET /subcategories/category/{category_id}
- Get subcategories for a specific category

POST /subcategories/
- Create subcategory
- Auth: Admin required

PUT /subcategories/{subcategory_id}
- Update subcategory
- Auth: Admin required

DELETE /subcategories/{subcategory_id}
- Delete subcategory
- Auth: Admin required
```

### Inventory (Products)
```
GET /inventory/
- Get all products (visible items only)
- Query params: status, pet_id, subtype_id, visibility

GET /inventory/{inventory_id}
- Get specific product

POST /inventory/
- Create product
- Auth: Admin required
- Body: {
    pet_id,
    product_name,
    product_image,
    price,
    stock,
    subtype_id,
    discount (0-100),
    rating,
    num_reviews,
    status (available, out_of_stock),
    visibility (true/false)
  }

PUT /inventory/{inventory_id}
- Update product (stock, price, discount, etc.)
- Auth: Admin required

DELETE /inventory/{inventory_id}
- Delete product
- Auth: Admin required
```

### Cart
```
GET /cart/
- Get or create user's cart
- Auth: Required

GET /cart/items
- Get all items in user's cart
- Auth: Required

POST /cart/items
- Add item to cart
- Auth: Required
- Body: { inventory_id, quantity }

PUT /cart/items/{cart_item_id}
- Update cart item quantity
- Auth: Required
- Body: { quantity }

DELETE /cart/items/{cart_item_id}
- Remove item from cart
- Auth: Required

DELETE /cart/clear
- Clear entire cart
- Auth: Required
```

### Wishlist
```
POST /wishlist/
- Add item to wishlist
- Auth: Required
- Body: { inventory_id }

GET /wishlist/
- Get user's wishlist
- Auth: Required

DELETE /wishlist/{wishlist_item_id}
- Remove item from wishlist
- Auth: Required

DELETE /wishlist/inventory/{inventory_id}
- Remove specific inventory from wishlist
- Auth: Required
```

### Orders
```
POST /orders/
- Create order from cart
- Auth: Required
- Body: {
    payment_type,
    first_name,
    last_name,
    email,
    address,
    city,
    zip_code
  }

GET /orders/
- Get user's orders
- Auth: Required

GET /orders/{order_id}
- Get specific order details
- Auth: Required

GET /orders/{order_id}/items
- Get items in specific order
- Auth: Required

GET /orders/all
- Get all orders (Admin only)
- Auth: Admin required

PUT /orders/{order_id}
- Update order status
- Auth: Admin required
- Body: { status }

DELETE /orders/{order_id}
- Delete order
- Auth: Admin required
```

### Admin Dashboard
```
GET /admin/dashboard/stats
- Get dashboard statistics
- Auth: Admin required
- Returns: {
    total_revenue,
    total_orders,
    pending_orders,
    total_users,
    active_users,
    low_stock_items
  }

GET /admin/dashboard/recent-orders
- Get recent 10 orders
- Auth: Admin required

GET /admin/inventory/low-stock
- Get items with low stock
- Auth: Admin required

GET /admin/users/stats
- Get user statistics
- Auth: Admin required

GET /admin/orders/stats
- Get order statistics by status
- Auth: Admin required

POST /admin/init-admin
- Initialize admin user (call once during setup)
- No auth required (first time only)
```

---

## 🔐 Authentication

### Getting a Token
```javascript
// Login
const response = await fetch('http://localhost:8000/users/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'admin@epet.com',
    password: 'admin1234'
  })
});

const data = await response.json();
// data.access_token is your JWT token
```

### Using Token in Requests
```javascript
const token = 'your-jwt-token-here';

fetch('http://localhost:8000/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 💾 Database Collections

```
- users              # User accounts with full_name, email, role
- pets               # Pet types (Dogs, Cats, Birds, Fishes)
- user_pet_profiles  # User's own pets with details
- categories         # Product categories by pet type
- subcategories      # Product subcategories (Accessories, Toys, Food)
- inventory          # Products with stock, price, discount, rating
- carts              # Shopping carts
- cart_items         # Items in carts
- orders             # Orders with shipping details
- order_items        # Items in orders
- wishlist           # User's wishlist items
```

---

## 🔄 Real-time Data Flow

### Creating an Order
1. User adds items to cart
2. User fills shipping info and creates order
3. Order is created with status "pending"
4. Cart items are cleared
5. Inventory stock is reduced
6. Admin can view new order in dashboard
7. Admin can update order status
8. User can see order in their order history

### Updating Inventory
1. Admin updates product (price, stock, discount)
2. Database is updated immediately
3. Frontend fetches updated product data
4. Users see updated prices/discounts on product page
5. Low stock alerts update automatically

---

## 🚀 Initialization Steps

### 1. Start MongoDB
```bash
mongod
```

### 2. Start Backend
```bash
uvicorn main:app --reload
```

### 3. Initialize Admin User
```bash
curl -X POST http://localhost:8000/admin/init-admin
```

Or visit: `http://localhost:8000/admin/init-admin`

### 4. Login as Admin
```
Username: admin@epet.com
Password: admin1234
```

### 5. Create Sample Data (Pet Types, Categories, Products)
Use the `/pets`, `/categories`, `/subcategories`, `/inventory` endpoints to create sample data.

---

## 📦 Order Statuses

- **pending** - Order created, awaiting confirmation
- **in_progress** - Order being processed
- **dispatched** - Order shipped
- **delivered** - Order received by customer
- **cancelled** - Order cancelled

---

## 🎯 Frontend Integration Checklist

- [ ] User signup with full_name
- [ ] User login with JWT token
- [ ] Display user's pet profiles in "My Pets" section
- [ ] Show pet profile edit/delete options
- [ ] Display product catalog with filters
- [ ] Show wishlist button on products
- [ ] Implement shopping cart
- [ ] Multi-step checkout with shipping form
- [ ] Order creation with shipping details
- [ ] Order history page
- [ ] Admin dashboard
- [ ] Admin inventory management
- [ ] Admin order status updates
- [ ] Real-time updates using API polling or WebSocket

---

## 🛠️ Development Notes

- All timestamps are in UTC
- IDs are MongoDB ObjectId (converted to string in responses)
- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes (configurable in .env)
- Admin operations are restricted by role checks
- Inventory visibility can be toggled for hidden products

---

## 📞 Support

For API documentation, visit: `http://localhost:8000/docs` (Swagger UI)
