# PawStore Backend - Complete Setup Guide

## ✅ Backend Setup Complete!

Your complete **PawStore Backend** with FastAPI + MongoDB is ready! 

---

## 🚀 Quick Start

### 1. Ensure MongoDB is Running
```powershell
mongod
```

### 2. Start the Backend Server
The server should already be running at: **http://127.0.0.1:8000**

If not, run:
```powershell
uvicorn main:app --reload
```

### 3. Initialize Sample Data (Optional)
```powershell
python init_sample_data.py
```

This will create:
- Admin user (admin@epet.com / admin1234)
- Sample regular users
- Pet types (Dogs, Cats, Birds, Fishes)
- Categories and subcategories
- Sample products with prices, discounts, ratings

### 4. Access the API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 📋 What's Included

### ✅ User Management
- User Registration (with full_name)
- User Login (JWT authentication)
- Role-based access (Admin vs Regular User)
- User profiles and management

### ✅ Pet Management
- Pet Types system (Dogs, Cats, Birds, Fishes)
- User Pet Profiles (My Pets section)
- Full pet details: name, breed, age, image, notes
- Edit/Delete pet profiles

### ✅ Product Catalog
- Categories by pet type
- Subcategories (Accessories, Toys, Food, etc.)
- Product inventory with:
  - Product name and image
  - Price and discounts
  - Stock tracking
  - Rating and reviews
  - Visibility toggle

### ✅ Shopping Features
- Shopping Cart management
- Wishlist functionality
- Multi-step Checkout:
  - Shipping Information (First Name, Last Name, Email, Address, City, ZIP)
  - Payment Method (Cash on Delivery - COD)
  - Order Review

### ✅ Order Management
- Order creation with shipping details
- Order status tracking (pending → in_progress → dispatched → delivered/cancelled)
- Order history for users
- Admin order management

### ✅ Admin Dashboard
- Dashboard Statistics:
  - Total Revenue
  - Total Orders (with pending count)
  - Total Users (with active count)
  - Low Stock Alerts
  - Recent Orders
- Inventory Management
- User Management
- Order Status Updates
- Low Stock Item Tracking

### ✅ Real-time Updates
When admin updates:
- **Inventory**: Stock, price, discount, visibility → immediately affects frontend
- **Order Status**: Changes → reflected in user orders and dashboard
- **Products**: All changes → synced to database instantly

---

## 🔑 Admin Credentials

```
Username: admin@epet.com
Password: admin1234
```

⚠️ **Change these in production!**

---

## 📁 Project Structure

```
epet-backend/
├── app/
│   ├── __init__.py
│   ├── auth.py                    # JWT & password hashing
│   ├── database.py                # MongoDB connection
│   ├── models.py                  # All Pydantic models
│   └── routes/
│       ├── __init__.py
│       ├── users.py               # User registration & login
│       ├── pets.py                # Pet types
│       ├── pet_profiles.py        # User pet profiles (My Pets)
│       ├── categories.py          # Product categories
│       ├── subcategories.py       # Product subcategories
│       ├── inventory.py           # Product management
│       ├── cart.py                # Shopping cart
│       ├── orders.py              # Orders & checkout
│       ├── wishlist.py            # Wishlist
│       └── admin.py               # Admin dashboard
├── main.py                        # FastAPI app entry point
├── requirements.txt               # Python dependencies
├── .env                          # Configuration
├── .env.example                  # Example configuration
├── .gitignore                    # Git ignore rules
├── README.md                     # Setup instructions
├── API_GUIDE.md                  # Detailed API documentation
├── SETUP_GUIDE.md               # This file
└── init_sample_data.py          # Sample data initialization script
```

---

## 🔌 API Endpoints Summary

### Authentication
```
POST   /users/register           - Register new user
POST   /users/login              - Login user
GET    /users/me                 - Get current user
```

### User Pet Profiles
```
POST   /pet-profiles/            - Create pet profile
GET    /pet-profiles/            - Get my pets
PUT    /pet-profiles/{id}        - Update pet
DELETE /pet-profiles/{id}        - Delete pet
```

### Shopping
```
GET    /inventory/               - Get products
POST   /inventory/               - Create product (Admin)
PUT    /inventory/{id}           - Update product (Admin)
DELETE /inventory/{id}           - Delete product (Admin)

POST   /cart/items               - Add to cart
GET    /cart/items               - Get cart items
PUT    /cart/items/{id}          - Update quantity
DELETE /cart/items/{id}          - Remove from cart

POST   /wishlist/                - Add to wishlist
GET    /wishlist/                - Get wishlist
DELETE /wishlist/{id}            - Remove from wishlist
```

### Checkout & Orders
```
POST   /orders/                  - Create order
GET    /orders/                  - Get my orders
GET    /orders/{id}              - Get order details
GET    /orders/{id}/items        - Get order items
PUT    /orders/{id}              - Update status (Admin)
```

### Admin
```
GET    /admin/dashboard/stats    - Dashboard statistics
GET    /admin/dashboard/recent-orders - Recent orders
GET    /admin/inventory/low-stock    - Low stock items
GET    /admin/users/stats           - User statistics
GET    /admin/orders/stats          - Order statistics
POST   /admin/init-admin            - Initialize admin
```

---

## 💾 Database Collections

| Collection | Purpose |
|-----------|---------|
| users | User accounts with roles |
| pets | Pet types (Dogs, Cats, etc.) |
| user_pet_profiles | User's own pet profiles |
| categories | Product categories by pet type |
| subcategories | Product subcategories |
| inventory | Products with stock & pricing |
| carts | User shopping carts |
| cart_items | Items in carts |
| orders | User orders with shipping |
| order_items | Items in orders |
| wishlist | User wishlist items |

---

## 🔄 Workflow Examples

### User Registration & Pet Creation
```
1. User registers → New user created in DB
2. User logs in → JWT token issued
3. User creates pet profile → Saved to user_pet_profiles
4. User can view/edit/delete pets
```

### Shopping Workflow
```
1. User browses products (GET /inventory/)
2. User adds items to cart (POST /cart/items)
3. User proceeds to checkout
4. User fills shipping info
5. Order is created → Cart cleared, inventory updated
6. Order appears in user's order history
```

### Admin Operations
```
1. Admin logs in with admin@epet.com
2. Admin accesses /admin/dashboard/stats
3. Admin can:
   - Update product inventory
   - Change order status
   - View user information
   - Monitor low stock items
4. Changes immediately sync to database
5. Users see updates on refresh
```

---

## 🔐 Security Features

✅ **Password Security**
- Passwords are hashed using bcrypt
- Never stored in plain text

✅ **Authentication**
- JWT tokens for secure sessions
- Token expiration after 30 minutes
- Bearer token in Authorization header

✅ **Authorization**
- Role-based access control (Admin vs User)
- Ownership verification for user data
- Admin-only endpoints protected

✅ **Data Validation**
- Pydantic models validate all inputs
- Email validation
- ObjectId validation

---

## 📊 Frontend Integration Checklist

### Authentication Pages
- [ ] Sign Up form (username, email, full_name, password)
- [ ] Sign In form
- [ ] Store JWT token in localStorage
- [ ] Add Authorization header to API requests

### User Pages
- [ ] User Profile/Dashboard
- [ ] My Pets page with add/edit/delete buttons
- [ ] Pet form modal with all fields

### Shopping Pages
- [ ] Product listing with filters
- [ ] Product card with image, price, discount, rating
- [ ] Add to Cart button
- [ ] Add to Wishlist button (heart icon)

### Cart & Checkout
- [ ] Shopping Cart page
- [ ] Shipping Information form
- [ ] Order Review page
- [ ] Order Success page

### Order Management
- [ ] Order History page
- [ ] Order Details page
- [ ] Order status display

### Admin Pages
- [ ] Admin Login redirect
- [ ] Dashboard with stats cards
- [ ] Inventory management table
- [ ] Order management table
- [ ] User management table
- [ ] Low stock alerts

---

## 🔧 Environment Variables

Located in `.env`:

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=epet_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5173
```

⚠️ **For Production:**
- Use a strong SECRET_KEY
- Update FRONTEND_URL to your domain
- Use MongoDB Atlas or managed database
- Enable HTTPS

---

## 🚨 Common Issues & Solutions

### Issue: "MongoDB connection refused"
**Solution**: Make sure MongoDB is running
```powershell
mongod
```

### Issue: "uvicorn command not found"
**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "Admin user already exists"
**Solution**: This is expected if you run init-admin twice. It's safe to ignore.

### Issue: "Port 8000 already in use"
**Solution**: Stop the running server or use a different port
```powershell
uvicorn main:app --reload --port 8001
```

---

## 📞 API Testing

### Using cURL
```bash
# Register user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@test.com","full_name":"John Doe","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@epet.com&password=admin1234"

# Get current user
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman
1. Import the API docs from http://127.0.0.1:8000/docs
2. Create a collection
3. Test endpoints with proper headers
4. Store token in Postman environment variable

### Using Swagger UI
1. Go to http://127.0.0.1:8000/docs
2. Click "Authorize" and login with admin@epet.com / admin1234
3. Click "Try it out" on any endpoint
4. Test directly in browser

---

## 📈 Production Deployment

### Before Deploying
- [ ] Change SECRET_KEY in .env
- [ ] Update FRONTEND_URL to production domain
- [ ] Use production MongoDB instance
- [ ] Enable HTTPS
- [ ] Set up proper error logging
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Use environment-specific settings

### Deployment Options
- **Heroku**: Simple cloud deployment
- **Railway**: Quick deployment
- **Render**: Modern alternative
- **AWS EC2**: Full control
- **DigitalOcean**: Affordable VPS
- **Docker**: Containerized deployment

---

## ✨ Next Steps

1. **Initialize sample data** (optional):
   ```powershell
   python init_sample_data.py
   ```

2. **Integrate with frontend**:
   - Update API_URL in frontend to http://localhost:8000
   - Implement authentication flow
   - Build UI pages based on screenshots

3. **Test all endpoints**:
   - Visit http://127.0.0.1:8000/docs
   - Test with Swagger UI

4. **Deploy when ready**:
   - Choose hosting platform
   - Configure environment variables
   - Deploy backend
   - Update frontend to use production API URL

---

## 📚 Documentation Files

- **README.md** - Basic setup and feature overview
- **API_GUIDE.md** - Detailed API endpoint documentation
- **SETUP_GUIDE.md** - This file, complete setup instructions

---

## ✅ Backend is Ready!

Your PawStore backend is complete and running. You now have:

✓ Full user authentication system
✓ Pet management system
✓ Complete e-commerce functionality
✓ Admin dashboard
✓ Real-time data synchronization
✓ Secure API with role-based access control

**Happy coding! 🚀**
