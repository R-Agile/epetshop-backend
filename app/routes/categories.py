from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import CategoryCreate, CategoryResponse, CategoryUpdate
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    category_dict = category.dict()
    result = await db.categories.insert_one(category_dict)
    category_dict["_id"] = str(result.inserted_id)
    
    return CategoryResponse(**category_dict)


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories():
    db = await get_database()
    categories = await db.categories.find().to_list(1000)
    
    for category in categories:
        category["_id"] = str(category["_id"])
    
    return [CategoryResponse(**category) for category in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    category = await db.categories.find_one({"_id": ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category["_id"] = str(category["_id"])
    return CategoryResponse(**category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    update_data = {k: v for k, v in category_update.dict(exclude_unset=True).items()}
    
    if update_data:
        result = await db.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
    
    category = await db.categories.find_one({"_id": ObjectId(category_id)})
    category["_id"] = str(category["_id"])
    return CategoryResponse(**category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    result = await db.categories.delete_one({"_id": ObjectId(category_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return None
