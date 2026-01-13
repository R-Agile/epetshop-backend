from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import WishlistItemCreate, WishlistItemResponse
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(item: WishlistItemCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    # Verify inventory item exists
    if not ObjectId.is_valid(item.inventory_id):
        raise HTTPException(status_code=400, detail="Invalid inventory ID")
    
    inventory = await db.inventory.find_one({"_id": ObjectId(item.inventory_id)})
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if already in wishlist
    existing = await db.wishlist.find_one({
        "user_id": user_id,
        "inventory_id": item.inventory_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    
    from datetime import datetime
    wishlist_item = {
        "user_id": user_id,
        "inventory_id": item.inventory_id,
        "created_at": datetime.utcnow()
    }
    
    result = await db.wishlist.insert_one(wishlist_item)
    wishlist_item["_id"] = str(result.inserted_id)
    
    return WishlistItemResponse(**wishlist_item)


@router.get("/", response_model=List[WishlistItemResponse])
async def get_my_wishlist(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    wishlist_items = await db.wishlist.find({"user_id": user_id}).to_list(1000)
    
    for item in wishlist_items:
        item["_id"] = str(item["_id"])
    
    return [WishlistItemResponse(**item) for item in wishlist_items]


@router.delete("/{wishlist_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(wishlist_item_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(wishlist_item_id):
        raise HTTPException(status_code=400, detail="Invalid wishlist item ID")
    
    # Check ownership
    item = await db.wishlist.find_one({"_id": ObjectId(wishlist_item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    
    if item["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.wishlist.delete_one({"_id": ObjectId(wishlist_item_id)})
    
    return None


@router.delete("/inventory/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_inventory_from_wishlist(inventory_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    
    result = await db.wishlist.delete_one({
        "user_id": user_id,
        "inventory_id": inventory_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    
    return None
