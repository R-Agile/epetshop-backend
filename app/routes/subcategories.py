from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import SubcategoryCreate, SubcategoryResponse, SubcategoryUpdate
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/subcategories", tags=["Subcategories"])


async def verify_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "super_user"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/", response_model=List[SubcategoryResponse])
async def get_all_subcategories():
    db = await get_database()
    
    subcategories = await db.subcategories.find().to_list(1000)
    
    for sub in subcategories:
        sub["_id"] = str(sub["_id"])
    
    return [SubcategoryResponse(**sub) for sub in subcategories]


@router.get("/category/{category_id}", response_model=List[SubcategoryResponse])
async def get_subcategories_by_category(category_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    subcategories = await db.subcategories.find({"category_id": category_id}).to_list(1000)
    
    for sub in subcategories:
        sub["_id"] = str(sub["_id"])
    
    return [SubcategoryResponse(**sub) for sub in subcategories]


@router.post("/", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_subcategory(subcategory: SubcategoryCreate, admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    # Verify category exists
    if not ObjectId.is_valid(subcategory.category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    category = await db.categories.find_one({"_id": ObjectId(subcategory.category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if subcategory already exists for this category
    existing = await db.subcategories.find_one({
        "name": subcategory.name.lower(),
        "category_id": subcategory.category_id
    })
    
    if existing:
        # Return existing subcategory instead of error (soft update)
        existing["_id"] = str(existing["_id"])
        return SubcategoryResponse(**existing)
    
    subcategory_dict = {
        "name": subcategory.name.lower(),
        "category_id": subcategory.category_id
    }
    
    result = await db.subcategories.insert_one(subcategory_dict)
    subcategory_dict["_id"] = str(result.inserted_id)
    
    return SubcategoryResponse(**subcategory_dict)


@router.put("/{subcategory_id}", response_model=SubcategoryResponse)
async def update_subcategory(
    subcategory_id: str,
    subcategory_update: SubcategoryUpdate,
    admin_user: dict = Depends(verify_admin)
):
    db = await get_database()
    
    if not ObjectId.is_valid(subcategory_id):
        raise HTTPException(status_code=400, detail="Invalid subcategory ID")
    
    update_data = {k: v for k, v in subcategory_update.dict(exclude_unset=True).items()}
    
    # Convert name to lowercase
    if "name" in update_data:
        update_data["name"] = update_data["name"].lower()
    
    if update_data:
        result = await db.subcategories.update_one(
            {"_id": ObjectId(subcategory_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Subcategory not found")
    
    subcategory = await db.subcategories.find_one({"_id": ObjectId(subcategory_id)})
    subcategory["_id"] = str(subcategory["_id"])
    return SubcategoryResponse(**subcategory)


@router.delete("/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subcategory(subcategory_id: str, admin_user: dict = Depends(verify_admin)):
    db = await get_database()
    
    if not ObjectId.is_valid(subcategory_id):
        raise HTTPException(status_code=400, detail="Invalid subcategory ID")
    
    result = await db.subcategories.delete_one({"_id": ObjectId(subcategory_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    return None
