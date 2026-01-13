from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import PetCreate, PetResponse, PetUpdate
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/pets", tags=["Pets"])


@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
async def create_pet(pet: PetCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    pet_dict = pet.dict()
    result = await db.pets.insert_one(pet_dict)
    pet_dict["_id"] = str(result.inserted_id)
    
    return PetResponse(**pet_dict)


@router.get("/", response_model=List[PetResponse])
async def get_all_pets():
    db = await get_database()
    pets = await db.pets.find().to_list(1000)
    
    for pet in pets:
        pet["_id"] = str(pet["_id"])
    
    return [PetResponse(**pet) for pet in pets]


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(pet_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(pet_id):
        raise HTTPException(status_code=400, detail="Invalid pet ID")
    
    pet = await db.pets.find_one({"_id": ObjectId(pet_id)})
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    pet["_id"] = str(pet["_id"])
    return PetResponse(**pet)


@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: str,
    pet_update: PetUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(pet_id):
        raise HTTPException(status_code=400, detail="Invalid pet ID")
    
    update_data = {k: v for k, v in pet_update.dict(exclude_unset=True).items()}
    
    if update_data:
        result = await db.pets.update_one(
            {"_id": ObjectId(pet_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pet not found")
    
    pet = await db.pets.find_one({"_id": ObjectId(pet_id)})
    pet["_id"] = str(pet["_id"])
    return PetResponse(**pet)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(pet_id):
        raise HTTPException(status_code=400, detail="Invalid pet ID")
    
    result = await db.pets.delete_one({"_id": ObjectId(pet_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    return None
