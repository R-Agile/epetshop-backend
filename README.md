# E-Pet Backend API

FastAPI backend for E-Pet application with MongoDB database.

## Tech Stack
- **Python 3.8+**
- **FastAPI** - Modern web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **JWT** - Authentication

## Project Structure
```
epet-backend/
├── app/
│   ├── routes/
│   │   ├── users.py
│   │   ├── pets.py
│   │   ├── categories.py
│   │   ├── subcategories.py
│   │   ├── inventory.py
│   │   ├── cart.py
│   │   └── orders.py
│   ├── models.py
│   ├── database.py
│   └── auth.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Install MongoDB
Make sure MongoDB is installed and running on your system.

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=epet_db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5173
```

### 6. Run the Application
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /users/register` - Register new user
- `POST /users/login` - Login user
- `GET /users/me` - Get current user info

### Users
- `GET /users/` - Get all users (auth required)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Pets
- `POST /pets/` - Create pet (auth required)
- `GET /pets/` - Get all pets
- `GET /pets/{pet_id}` - Get pet by ID
- `PUT /pets/{pet_id}` - Update pet
- `DELETE /pets/{pet_id}` - Delete pet

### Categories
- `POST /categories/` - Create category (auth required)
- `GET /categories/` - Get all categories
- `GET /categories/{category_id}` - Get category by ID
- `PUT /categories/{category_id}` - Update category
- `DELETE /categories/{category_id}` - Delete category

### Subcategories
- `POST /subcategories/` - Create subcategory (auth required)
- `GET /subcategories/` - Get all subcategories
- `GET /subcategories/category/{category_id}` - Get subcategories by category
- `GET /subcategories/{subcategory_id}` - Get subcategory by ID
- `PUT /subcategories/{subcategory_id}` - Update subcategory
- `DELETE /subcategories/{subcategory_id}` - Delete subcategory

### Inventory
- `POST /inventory/` - Create inventory item (auth required)
- `GET /inventory/` - Get all inventory (with filters)
- `GET /inventory/{inventory_id}` - Get inventory item by ID
- `PUT /inventory/{inventory_id}` - Update inventory item
- `DELETE /inventory/{inventory_id}` - Delete inventory item

### Cart
- `GET /cart/` - Get or create user cart (auth required)
- `GET /cart/items` - Get cart items
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{cart_item_id}` - Update cart item quantity
- `DELETE /cart/items/{cart_item_id}` - Remove item from cart
- `DELETE /cart/clear` - Clear cart

### Orders
- `POST /orders/` - Create order from cart (auth required)
- `GET /orders/` - Get user orders
- `GET /orders/all` - Get all orders (admin only)
- `GET /orders/{order_id}` - Get order by ID
- `GET /orders/{order_id}/items` - Get order items
- `PUT /orders/{order_id}` - Update order (admin only)
- `DELETE /orders/{order_id}` - Delete order (admin only)

## Frontend Integration

### 1. Install Axios in Frontend
```bash
npm install axios
```

### 2. Create API Client
Create `src/lib/api.js`:
```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 3. Example Usage
```javascript
import api from './lib/api';

// Register
const register = async (userData) => {
  const response = await api.post('/users/register', userData);
  return response.data;
};

// Login
const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await api.post('/users/login', formData);
  localStorage.setItem('token', response.data.access_token);
  return response.data;
};

// Get inventory
const getInventory = async () => {
  const response = await api.get('/inventory/');
  return response.data;
};

// Add to cart
const addToCart = async (cartItem) => {
  const response = await api.post('/cart/items', cartItem);
  return response.data;
};
```

## Database Schema

The application uses the following MongoDB collections:
- `users` - User accounts
- `pets` - Pet types
- `categories` - Product categories
- `subcategories` - Product subcategories
- `inventory` - Available products
- `carts` - User shopping carts
- `cart_items` - Items in carts
- `orders` - User orders
- `order_items` - Items in orders
- `users_pets` - User-pet associations

## Development

### Adding New Routes
1. Create new route file in `app/routes/`
2. Define endpoints using FastAPI router
3. Import and include router in `main.py`

### Testing
Use the Swagger UI at `/docs` to test all endpoints interactively.

## Production Deployment

1. Change `SECRET_KEY` in `.env` to a secure random string
2. Update `FRONTEND_URL` to your production frontend URL
3. Update CORS settings in `main.py` to only allow your frontend domain
4. Use a production MongoDB instance
5. Deploy using services like:
   - Heroku
   - AWS EC2
   - DigitalOcean
   - Railway
   - Render

## License
MIT
