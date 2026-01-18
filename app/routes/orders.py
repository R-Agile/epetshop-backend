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
    print(f"\n=== Creating order for user_id: {user_id} ===")
    print(f"User email: {current_user.get('email')}, Role: {current_user.get('role')}")
    
    cart = await db.carts.find_one({"user_id": user_id})
    
    if not cart:
        print(f"❌ No cart found for user_id: {user_id}")
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart_id = str(cart["_id"])
    print(f"✓ Found cart_id: {cart_id}")
    
    cart_items = await db.cart_items.find({"cart_id": cart_id}).to_list(1000)
    
    print(f"✓ Cart items count: {len(cart_items)}")
    if not cart_items:
        print(f"❌ No cart items found for cart_id: {cart_id}")
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate subtotal and order items
    subtotal = 0.0
    order_items_list = []
    
    for cart_item in cart_items:
        inventory = await db.inventory.find_one({"_id": ObjectId(cart_item["inventory_id"])})
        if inventory:
            item_total = float(inventory["price"]) * cart_item["quantity"]
            subtotal += item_total
            
            order_items_list.append({
                "inventory_id": cart_item["inventory_id"],
                "price": float(inventory["price"]),
                "quantity": cart_item["quantity"]
            })
    
    # Calculate delivery charges: Rs 300 if subtotal < 2000, else free
    delivery_charges = 300.0 if subtotal < 2000 else 0.0
    total = subtotal + delivery_charges
    
    # Create order
    order_dict = {
        "user_id": user_id,
        "order_time": datetime.utcnow(),
        "payment_type": order.payment_type,
        "status": "pending",
        "first_name": order.first_name,
        "last_name": order.last_name,
        "email": order.email,
        "phone": order.phone,
        "address": order.address,
        "city": order.city,
        "zip_code": order.zip_code,
        "subtotal": subtotal,
        "delivery_charges": delivery_charges,
        "total": total
    }
    
    result = await db.orders.insert_one(order_dict)
    order_id = str(result.inserted_id)
    
    # Create order items from cart items
    for order_item_data in order_items_list:
        inventory = await db.inventory.find_one({"_id": ObjectId(order_item_data["inventory_id"])})
        
        order_item = {
            "order_id": order_id,
            "inventory_id": str(order_item_data["inventory_id"]),
            "price": float(order_item_data["price"]),
            "quantity": int(order_item_data["quantity"]),
            "product_name": inventory.get("name", "Product") if inventory else "Product",
            "product_image": inventory.get("images", [None])[0] if inventory and inventory.get("images") else "https://via.placeholder.com/100"
        }
        result = await db.order_items.insert_one(order_item)
        order_item["_id"] = str(result.inserted_id)
        
        # Update inventory stock
        if inventory:
            new_stock = inventory["stock"] - order_item_data["quantity"]
            await db.inventory.update_one(
                {"_id": ObjectId(order_item_data["inventory_id"])},
                {"$set": {"stock": new_stock}}
            )
    
    # Clear cart
    await db.cart_items.delete_many({"cart_id": cart_id})
    
    order_dict["_id"] = order_id
    return OrderResponse(**order_dict)


@router.get("/")
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    orders = await db.orders.find({"user_id": user_id}).to_list(1000)
    
    result = []
    for order in orders:
        # Create response dict with all fields
        order_data = dict(order)
        order_data["_id"] = str(order["_id"])
        order_data["id"] = str(order["_id"])
        # Remove _id from dict to avoid duplication
        del order_data["_id"]
        result.append(order_data)
    
    return result


@router.get("/all")
async def get_all_orders(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Only admin or super_user can see all orders
    if current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    orders = await db.orders.find().to_list(1000)
    
    result = []
    for order in orders:
        # Create response dict with all fields
        order_data = dict(order)
        order_data["_id"] = str(order["_id"])
        order_data["id"] = str(order["_id"])
        # Remove _id from dict to avoid duplication
        del order_data["_id"]
        result.append(order_data)
    
    return result


@router.get("/{order_id}")
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order or is admin
    if str(order["user_id"]) != str(current_user["_id"]) and current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order_data = dict(order)
    order_data["_id"] = str(order["_id"])
    order_data["id"] = str(order["_id"])
    del order_data["_id"]
    return order_data


@router.get("/{order_id}/items")
async def get_order_items(order_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    # Verify order exists and user has access
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if str(order["user_id"]) != str(current_user["_id"]) and current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order_items = await db.order_items.find({"order_id": order_id}).to_list(1000)
    
    result = []
    for item in order_items:
        item_data = dict(item)
        item_data["_id"] = str(item["_id"])
        item_data["id"] = str(item["_id"])
        del item_data["_id"]
        result.append(item_data)
    
    return result


@router.put("/{order_id}")
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    # Only admin or super_user can update orders
    if current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    current_status = order.get("status", "pending")
    terminal_statuses = ["delivered", "cancelled"]
    allowed_statuses = ["pending", "in_progress", "dispatched", "delivered", "cancelled"]

    update_data = {k: v for k, v in order_update.dict(exclude_unset=True).items()}
    
    # Validate status transitions: delivered/cancelled are terminal
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status not in allowed_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        if current_status in terminal_statuses and new_status != current_status:
            raise HTTPException(status_code=400, detail="Cannot change status after it is delivered or cancelled")
    
    # If already terminal and no other fields to update, just return current order
    if current_status in terminal_statuses and (not update_data or (len(update_data) == 1 and "status" in update_data)):
        order_data = dict(order)
        order_data["_id"] = str(order["_id"])
        order_data["id"] = str(order["_id"])
        del order_data["_id"]
        return order_data
    
    if update_data:
        result = await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
    
    # Fetch updated order
    updated_order = await db.orders.find_one({"_id": ObjectId(order_id)})
    order_data = dict(updated_order)
    order_data["_id"] = str(updated_order["_id"])
    order_data["id"] = str(updated_order["_id"])
    del order_data["_id"]
    return order_data


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    # Only admin or super_user can delete orders
    if current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete order items first
    await db.order_items.delete_many({"order_id": order_id})
    
    # Delete order
    result = await db.orders.delete_one({"_id": ObjectId(order_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return None
