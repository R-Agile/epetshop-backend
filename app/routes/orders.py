from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from datetime import datetime
from app.models import (
    OrderCreate, OrderResponse, OrderUpdate,
    OrderItemCreate, OrderItemResponse
)
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Check if user is banned
    if current_user.get("status") == "banned":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been banned. You cannot place orders."
        )
    
    # Get user's cart items
    user_id = str(current_user["_id"])
    cart = await db.carts.find_one({"user_id": user_id})
    
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart_id = str(cart["_id"])
    cart_items = await db.cart_items.find({"cart_id": cart_id}).to_list(1000)
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Create order
    order_dict = {
        "user_id": user_id,
        "order_time": datetime.utcnow(),
        "payment_type": order.payment_type,
        "status": "pending",
        "first_name": order.first_name,
        "last_name": order.last_name,
        "email": order.email,
        "address": order.address,
        "city": order.city,
        "zip_code": order.zip_code
    }
    
    result = await db.orders.insert_one(order_dict)
    order_id = str(result.inserted_id)
    
    # Create order items from cart items
    for cart_item in cart_items:
        inventory = await db.inventory.find_one({"_id": ObjectId(cart_item["inventory_id"])})
        if inventory:
            order_item = {
                "order_id": order_id,
                "inventory_id": cart_item["inventory_id"],
                "price": inventory["price"],
                "quantity": cart_item["quantity"]
            }
            await db.order_items.insert_one(order_item)
            
            # Update inventory stock
            new_stock = inventory["stock"] - cart_item["quantity"]
            await db.inventory.update_one(
                {"_id": ObjectId(cart_item["inventory_id"])},
                {"$set": {"stock": new_stock}}
            )
    
    # Clear cart
    await db.cart_items.delete_many({"cart_id": cart_id})
    
    order_dict["_id"] = order_id
    return OrderResponse(**order_dict)


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    orders = await db.orders.find({"user_id": user_id}).to_list(1000)
    
    for order in orders:
        order["_id"] = str(order["_id"])
    
    return [OrderResponse(**order) for order in orders]


@router.get("/all", response_model=List[OrderResponse])
async def get_all_orders(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Only admin can see all orders
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    orders = await db.orders.find().to_list(1000)
    
    for order in orders:
        order["_id"] = str(order["_id"])
    
    return [OrderResponse(**order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order or is admin
    if str(order["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order["_id"] = str(order["_id"])
    return OrderResponse(**order)


@router.get("/{order_id}/items", response_model=List[OrderItemResponse])
async def get_order_items(order_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    # Verify order exists and user has access
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if str(order["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order_items = await db.order_items.find({"order_id": order_id}).to_list(1000)
    
    for item in order_items:
        item["_id"] = str(item["_id"])
    
    return [OrderItemResponse(**item) for item in order_items]


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    # Only admin can update orders
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {k: v for k, v in order_update.dict(exclude_unset=True).items()}
    
    if update_data:
        result = await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
    
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    order["_id"] = str(order["_id"])
    return OrderResponse(**order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    # Only admin can delete orders
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete order items first
    await db.order_items.delete_many({"order_id": order_id})
    
    # Delete order
    result = await db.orders.delete_one({"_id": ObjectId(order_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return None
