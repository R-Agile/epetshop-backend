from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
from app.models import DashboardStats, RecentOrder
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


async def verify_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    # Total Orders
    total_orders_count = await db.orders.count_documents({})
    pending_orders_count = await db.orders.count_documents({"status": "pending"})
    
    # Total Revenue
    orders = await db.orders.find().to_list(None)
    total_revenue = 0.0
    for order in orders:
        order_items = await db.order_items.find({"order_id": str(order["_id"])}).to_list(None)
        for item in order_items:
            total_revenue += item["price"] * item["quantity"]
    
    # Total Users
    total_users_count = await db.users.count_documents({})
    active_users_count = await db.users.count_documents({"last_login_time": {"$ne": None}})
    
    # Low Stock Items (less than 10 units)
    low_stock_count = await db.inventory.count_documents({"stock": {"$lt": 10}})
    
    return DashboardStats(
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders_count,
        pending_orders=pending_orders_count,
        total_users=total_users_count,
        active_users=active_users_count,
        low_stock_items=low_stock_count
    )


@router.get("/dashboard/recent-orders", response_model=List[RecentOrder])
async def get_recent_orders(admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    orders = await db.orders.find().sort("order_time", -1).limit(10).to_list(10)
    
    recent_orders = []
    for order in orders:
        # Get user details
        user = await db.users.find_one({"_id": ObjectId(order["user_id"])})
        
        # Calculate total
        order_items = await db.order_items.find({"order_id": str(order["_id"])}).to_list(None)
        total = sum(item["price"] * item["quantity"] for item in order_items)
        
        recent_orders.append(RecentOrder(
            _id=str(order["_id"]),
            customer_name=user.get("full_name", "Unknown") if user else "Unknown",
            customer_email=user.get("email", "") if user else "",
            total=round(total, 2),
            status=order["status"],
            date=order["order_time"]
        ))
    
    return recent_orders


@router.get("/inventory/low-stock")
async def get_low_stock_items(admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    low_stock_items = await db.inventory.find({"stock": {"$lt": 10}}).to_list(None)
    
    result = []
    for item in low_stock_items:
        result.append({
            "id": str(item["_id"]),
            "product_name": item.get("product_name", "Unknown"),
            "stock": item["stock"],
            "status": "Low Stock" if item["stock"] < 10 else "Out of Stock"
        })
    
    return result


@router.get("/users/stats")
async def get_user_statistics(admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"last_login_time": {"$ne": None}})
    inactive_users = total_users - active_users
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users
    }


@router.get("/orders/stats")
async def get_order_statistics(admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    statuses = ["pending", "in_progress", "dispatched", "delivered", "cancelled"]
    stats = {}
    
    for status in statuses:
        count = await db.orders.count_documents({"status": status})
        stats[status] = count
    
    return stats


@router.post("/init-admin")
async def initialize_admin():
    """Initialize admin user - call this once during setup"""
    db = await get_database()
    from app.auth import get_password_hash
    
    # Check if admin already exists
    admin = await db.users.find_one({"username": "admin@epet.com"})
    if admin:
        return {"message": "Admin user already exists"}
    
    # Create admin user
    admin_dict = {
        "username": "admin@epet.com",
        "email": "admin@epet.com",
        "full_name": "Admin User",
        "password_hash": get_password_hash("admin1234"),
        "role": "admin",
        "register_time": datetime.utcnow(),
        "last_login_time": None
    }
    
    result = await db.users.insert_one(admin_dict)
    
    return {
        "message": "Admin user created successfully",
        "username": "admin@epet.com",
        "password": "admin1234",
        "id": str(result.inserted_id)
    }
