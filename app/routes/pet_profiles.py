from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import UserPetProfileCreate, UserPetProfileResponse, UserPetProfileUpdate
from app.database import get_database
from app.routes.users import get_current_user

router = APIRouter(prefix="/pet-profiles", tags=["Pet Profiles"])


@router.post("/", response_model=UserPetProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_pet_profile(pet_profile: UserPetProfileCreate, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user_id = str(current_user["_id"])
    username = current_user.get("username", "")
    
    pet_profile_dict = pet_profile.dict()
    pet_profile_dict["user_id"] = user_id
    pet_profile_dict["username"] = username
    from datetime import datetime
    pet_profile_dict["created_at"] = datetime.utcnow()
    
    result = await db.user_pet_profiles.insert_one(pet_profile_dict)
    pet_profile_dict["_id"] = str(result.inserted_id)
    
    return UserPetProfileResponse(**pet_profile_dict)


@router.get("/user/{user_id}", response_model=List[UserPetProfileResponse])
async def get_user_pet_profiles(user_id: str):
    """Get all pet profiles for a specific user (no auth required for viewing)"""
    db = await get_database()
    
    pet_profiles = await db.user_pet_profiles.find({"user_id": user_id}).to_list(1000)
    
    for profile in pet_profiles:
        profile["_id"] = str(profile["_id"])
    
    return [UserPetProfileResponse(**profile) for profile in pet_profiles]


@router.get("/{pet_profile_id}", response_model=UserPetProfileResponse)
async def get_pet_profile(pet_profile_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(pet_profile_id):
        raise HTTPException(status_code=400, detail="Invalid pet profile ID")
    
    pet_profile = await db.user_pet_profiles.find_one({"_id": ObjectId(pet_profile_id)})
    if not pet_profile:
        raise HTTPException(status_code=404, detail="Pet profile not found")
    
    # Check ownership
    if pet_profile["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    pet_profile["_id"] = str(pet_profile["_id"])
    return UserPetProfileResponse(**pet_profile)


@router.put("/{pet_profile_id}", response_model=UserPetProfileResponse)
async def update_pet_profile(
    pet_profile_id: str,
    pet_profile_update: UserPetProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(pet_profile_id):
        raise HTTPException(status_code=400, detail="Invalid pet profile ID")
    
    # Check ownership
    pet_profile = await db.user_pet_profiles.find_one({"_id": ObjectId(pet_profile_id)})
    if not pet_profile:
        raise HTTPException(status_code=404, detail="Pet profile not found")
    
    if pet_profile["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {k: v for k, v in pet_profile_update.dict(exclude_unset=True).items()}
    
    if update_data:
        await db.user_pet_profiles.update_one(
            {"_id": ObjectId(pet_profile_id)},
            {"$set": update_data}
        )
    
    pet_profile = await db.user_pet_profiles.find_one({"_id": ObjectId(pet_profile_id)})
    pet_profile["_id"] = str(pet_profile["_id"])
    return UserPetProfileResponse(**pet_profile)


@router.delete("/{pet_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet_profile(pet_profile_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(pet_profile_id):
        raise HTTPException(status_code=400, detail="Invalid pet profile ID")
    
    # Check ownership
    pet_profile = await db.user_pet_profiles.find_one({"_id": ObjectId(pet_profile_id)})
    if not pet_profile:
        raise HTTPException(status_code=404, detail="Pet profile not found")
    
    if pet_profile["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.user_pet_profiles.delete_one({"_id": ObjectId(pet_profile_id)})
    
    return None
