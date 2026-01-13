from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from bson import ObjectId
from app.models import InventoryCreate, InventoryResponse, InventoryUpdate
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


async def verify_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(inventory: InventoryCreate, admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    # Verify category exists
    if not ObjectId.is_valid(inventory.category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    category = await db.categories.find_one({"_id": ObjectId(inventory.category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category is coming soon
    if category.get("coming_soon"):
        raise HTTPException(status_code=400, detail="Cannot add products to categories marked as 'Coming Soon'")
    
    inventory_dict = inventory.dict()
    result = await db.inventory.insert_one(inventory_dict)
    inventory_dict["_id"] = str(result.inserted_id)
    
    return InventoryResponse(**inventory_dict)


@router.get("/", response_model=List[InventoryResponse])
async def get_all_inventory(
    category_id: Optional[str] = None,
    subcategory_id: Optional[str] = None,
    is_visible: Optional[bool] = None
):
    db = await get_database()
    
    query = {}
    
    if category_id:
        query["category_id"] = category_id
    if subcategory_id:
        query["subcategory_id"] = subcategory_id
    if is_visible is not None:
        query["is_visible"] = is_visible
    
    inventory_items = await db.inventory.find(query).to_list(1000)
    
    for item in inventory_items:
        item["_id"] = str(item["_id"])
    
    return [InventoryResponse(**item) for item in inventory_items]


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_item(inventory_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(inventory_id):
        raise HTTPException(status_code=400, detail="Invalid inventory ID")
    
    item = await db.inventory.find_one({"_id": ObjectId(inventory_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    item["_id"] = str(item["_id"])
    return InventoryResponse(**item)


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory_item(
    inventory_id: str,
    inventory_update: InventoryUpdate,
    admin_user: dict = Depends(verify_admin)
):
    db = await get_database()
    
    if not ObjectId.is_valid(inventory_id):
        raise HTTPException(status_code=400, detail="Invalid inventory ID")
    
    update_data = {k: v for k, v in inventory_update.dict(exclude_unset=True).items()}
    
    if update_data:
        result = await db.inventory.update_one(
            {"_id": ObjectId(inventory_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Inventory item not found")
    
    item = await db.inventory.find_one({"_id": ObjectId(inventory_id)})
    item["_id"] = str(item["_id"])
    return InventoryResponse(**item)


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(inventory_id: str, admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    if not ObjectId.is_valid(inventory_id):
        raise HTTPException(status_code=400, detail="Invalid inventory ID")
    
    result = await db.inventory.delete_one({"_id": ObjectId(inventory_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    return None
