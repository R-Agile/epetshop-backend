from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import (
    CartResponse, CartItemCreate, CartItemResponse, 
    CartItemUpdate
)
from app.database import get_database
from app.routes.users import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/cart", tags=["Cart"])

# Model for guest cart sync
class CartSyncRequest(BaseModel):
    items: List[dict]


@router.get("/", response_model=CartResponse)
async def get_or_create_cart(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    # Check if cart exists
    cart = await db.carts.find_one({"user_id": user_id})
    
    if not cart:
        # Create new cart
        from datetime import datetime
        cart_dict = {
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        result = await db.carts.insert_one(cart_dict)
        cart_dict["_id"] = str(result.inserted_id)
        return CartResponse(**cart_dict)
    
    cart["_id"] = str(cart["_id"])
    return CartResponse(**cart)


@router.get("/items", response_model=List[CartItemResponse])
async def get_cart_items(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    # Get user's cart
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        return []
    
    cart_id = str(cart["_id"])
    
    # Get cart items
    cart_items = await db.cart_items.find({"cart_id": cart_id}).to_list(1000)
    
    for item in cart_items:
        item["_id"] = str(item["_id"])
    
    return [CartItemResponse(**item) for item in cart_items]


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(cart_item: CartItemCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    print(f"Adding to cart for user_id: {user_id}")
    print(f"Cart item data: inventory_id={cart_item.inventory_id}, quantity={cart_item.quantity}")
    
    # Get or create cart
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        from datetime import datetime
        cart_dict = {
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        result = await db.carts.insert_one(cart_dict)
        cart_id = str(result.inserted_id)
        print(f"Created new cart with cart_id: {cart_id}")
    else:
        cart_id = str(cart["_id"])
        print(f"Using existing cart_id: {cart_id}")
    
    # Verify inventory item exists
    if not ObjectId.is_valid(cart_item.inventory_id):
        print(f"Invalid inventory ID format: {cart_item.inventory_id}")
        raise HTTPException(status_code=400, detail="Invalid inventory ID")
    
    inventory = await db.inventory.find_one({"_id": ObjectId(cart_item.inventory_id)})
    if not inventory:
        print(f"Inventory item not found: {cart_item.inventory_id}")
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if item already in cart
    existing_item = await db.cart_items.find_one({
        "cart_id": cart_id,
        "inventory_id": cart_item.inventory_id
    })
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item["quantity"] + cart_item.quantity
        await db.cart_items.update_one(
            {"_id": existing_item["_id"]},
            {"$set": {"quantity": new_quantity}}
        )
        existing_item["_id"] = str(existing_item["_id"])
        existing_item["quantity"] = new_quantity
        return CartItemResponse(**existing_item)
    
    # Add new item
    cart_item_dict = cart_item.dict()
    cart_item_dict["cart_id"] = cart_id
    result = await db.cart_items.insert_one(cart_item_dict)
    cart_item_dict["_id"] = str(result.inserted_id)
    
    return CartItemResponse(**cart_item_dict)


@router.put("/items/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: str,
    cart_item_update: CartItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(cart_item_id):
        raise HTTPException(status_code=400, detail="Invalid cart item ID")
    
    update_data = {k: v for k, v in cart_item_update.dict(exclude_unset=True).items()}
    
    if update_data:
        result = await db.cart_items.update_one(
            {"_id": ObjectId(cart_item_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
    
    item = await db.cart_items.find_one({"_id": ObjectId(cart_item_id)})
    item["_id"] = str(item["_id"])
    return CartItemResponse(**item)


@router.delete("/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(cart_item_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(cart_item_id):
        raise HTTPException(status_code=400, detail="Invalid cart item ID")
    
    result = await db.cart_items.delete_one({"_id": ObjectId(cart_item_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return None


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    # Get user's cart
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        return None
    
    cart_id = str(cart["_id"])
    
    # Delete all cart items
    await db.cart_items.delete_many({"cart_id": cart_id})
    
    return None


# ============= GUEST CART ENDPOINTS (GuestId Based) =============

@router.get("/{guest_id}")
async def get_guest_cart(guest_id: str):
    """Get cart items for a guest using guestId"""
    db = await get_database()
    
    # Find guest cart
    cart = await db.carts.find_one({"guest_id": guest_id})
    
    if not cart:
        return {"items": []}
    
    # Get cart items
    cart_items = await db.cart_items.find({"cart_id": str(cart["_id"])}).to_list(1000)
    
    # Format items with product details
    formatted_items = []
    for item in cart_items:
        formatted_items.append({
            "id": str(item["_id"]),
            "product_id": item.get("inventory_id"),
            "quantity": item.get("quantity", 1),
            "product": item.get("product", {})
        })
    
    return {"items": formatted_items}


@router.post("/{guest_id}/sync")
async def sync_guest_cart(guest_id: str, request: CartSyncRequest):
    """Sync guest cart items to database"""
    db = await get_database()
    from datetime import datetime
    
    try:
        # Get or create cart for guest
        cart = await db.carts.find_one({"guest_id": guest_id})
        
        if not cart:
            # Create new guest cart
            cart_dict = {
                "guest_id": guest_id,
                "user_id": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await db.carts.insert_one(cart_dict)
            cart_id = str(result.inserted_id)
        else:
            cart_id = str(cart["_id"])
            # Update timestamp
            await db.carts.update_one(
                {"_id": ObjectId(cart_id)},
                {"$set": {"updated_at": datetime.utcnow()}}
            )
        
        # Clear existing items
        await db.cart_items.delete_many({"cart_id": cart_id})
        
        # Add new items
        for item in request.items:
            cart_item = {
                "cart_id": cart_id,
                "inventory_id": item.get("product", {}).get("id"),
                "product": item.get("product", {}),
                "quantity": item.get("quantity", 1),
                "created_at": datetime.utcnow()
            }
            await db.cart_items.insert_one(cart_item)
        
        return {"status": "success", "message": "Cart synced to database"}
    
    except Exception as e:
        print(f"Error syncing cart: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.delete("/{guest_id}")
async def clear_guest_cart(guest_id: str):
    """Clear guest cart"""
    db = await get_database()
    
    cart = await db.carts.find_one({"guest_id": guest_id})
    if cart:
        cart_id = str(cart["_id"])
        await db.cart_items.delete_many({"cart_id": cart_id})
    
    return {"status": "success"}
