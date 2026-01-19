from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from datetime import datetime, timedelta
from bson import ObjectId
import base64
import json
from pydantic import BaseModel
from app.models import (
    UserCreate, UserResponse, UserUpdate, Token, LoginRequest, ChangePasswordRequest, 
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.database import get_database
from app.auth import get_password_hash, verify_password, create_access_token, verify_token
from app.database import settings
from app.email import send_password_reset_email, verify_reset_token

router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

class AvatarUpdate(BaseModel):
    avatar: str


def decrypt_data(encrypted: str, key: str = "pawstore_secret_key") -> str:
    """Decrypt XOR encrypted data"""
    data = base64.b64decode(encrypted).decode('latin-1')
    result = ''
    for i in range(len(data)):
        result += chr(ord(data[i]) ^ ord(key[i % len(key)]))
    return result


def encrypt_data(data: str, key: str = "pawstore_secret_key") -> str:
    """Encrypt data using XOR cipher"""
    result = ''
    for i in range(len(data)):
        result += chr(ord(data[i]) ^ ord(key[i % len(key)]))
    return base64.b64encode(result.encode('latin-1')).decode('utf-8')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    db = await get_database()
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    db = await get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"email": user.email}, {"username": user.username}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user_dict = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password_hash": get_password_hash(user.password),
        "role": user.role,
        "status": "active",
        "register_time": datetime.utcnow(),
        "last_login_time": None
    }
    
    result = await db.users.insert_one(user_dict)
    user_id = str(result.inserted_id)
    
    # Create access token for auto-login after registration
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "_id": user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.post("/login")
async def login(login_data: LoginRequest):
    db = await get_database()
    
    # Handle encrypted credentials
    if login_data.encrypted:
        try:
            decrypted = decrypt_data(login_data.encrypted)
            credentials = json.loads(decrypted)
            email = credentials.get('email')
            password = credentials.get('password')
        except Exception as e:
            print(f"Decryption error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid encrypted data: {str(e)}",
            )
    else:
        # Fallback to plain credentials (for backward compatibility)
        email = login_data.email
        password = login_data.password
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    
    # Find user by email
    user = await db.users.find_one({"email": email.lower()})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is banned
    if user.get("status") == "banned":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been banned. Please contact support.",
        )
    
    # Verify password
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_time": datetime.utcnow()}}
    )
    
    # Admin/super_user gets 2 hours token expiry, regular users get default
    if user.get("role") in ["admin", "super_user"]:
        access_token_expires = timedelta(minutes=120)  # 2 hours for admins
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Prepare response data
    response_data = {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "_id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "status": user.get("status", "active")
        }
    }
    
    # Encrypt response data
    encrypted_response = encrypt_data(json.dumps(response_data))
    
    return {
        "encrypted_response": encrypted_response
    }


@router.post("/login-plain")
async def login_plain(login_data: LoginRequest):
    """Temporary endpoint for testing without encryption"""
    db = await get_database()
    
    email = login_data.email
    password = login_data.password
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    
    # Find user by email
    user = await db.users.find_one({"email": email.lower()})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Update last login time
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_time": datetime.utcnow()}}
    )
    
    # Admin/super_user gets 2 hours token expiry, regular users get default
    if user.get("role") in ["admin", "super_user"]:
        access_token_expires = timedelta(minutes=120)  # 2 hours for admins
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "_id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "status": user.get("status", "active")
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    current_user["_id"] = str(current_user["_id"])
    return UserResponse(**current_user)


@router.get("/", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    # Only super_user can see all users
    if current_user.get("role") not in ["super_user", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized. Admin access required.")
    
    db = await get_database()
    # Only fetch regular users, exclude admin and super_user
    users = await db.users.find({"role": "user"}).to_list(1000)
    
    for user in users:
        user["_id"] = str(user["_id"])
    
    return [UserResponse(**user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return UserResponse(**user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Check if user is admin
    if current_user.get("role") not in ["super_user", "admin"]:
        raise HTTPException(status_code=403, detail="Only admin can update users")
    
    # Get current user data
    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items()}
    
    if update_data:
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Get updated user
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    user["_id"] = str(user["_id"])
    return UserResponse(**user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return None


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change password for authenticated user"""
    db = await get_database()
    
    print(f"[DEBUG] Change password request for user: {current_user.get('email')}")
    print(f"[DEBUG] Old password provided: {bool(request.old_password)}")
    
    # Verify old password
    if not verify_password(request.old_password, current_user["password_hash"]):
        print(f"[DEBUG] Old password verification failed for user: {current_user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    print(f"[DEBUG] Old password verified successfully")
    
    # Hash new password
    new_password_hash = get_password_hash(request.new_password)
    
    # Update password
    result = await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    print(f"[DEBUG] Password update result: matched={result.matched_count}, modified={result.modified_count}")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email to user"""
    db = await get_database()
    
    # Check if user exists
    user = await db.users.find_one({"email": request.email.lower()})
    if not user:
        # Don't reveal if email exists - for security
        return {"message": "If an account exists with this email, password reset instructions have been sent"}
    
    # Send password reset email
    await send_password_reset_email(request.email)
    
    return {"message": "If an account exists with this email, password reset instructions have been sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using email and token from reset link"""
    db = await get_database()
    
    # Verify token
    if not verify_reset_token(request.email, request.token if hasattr(request, 'token') else None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link"
        )
    
    # Find user by email
    user = await db.users.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hash new password
    new_password_hash = get_password_hash(request.new_password)
    
    # Update password
    result = await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Password reset successfully"}


@router.get("/user/{user_id}/summary")
async def get_user_summary(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's total orders and total spent"""
    from app.database import get_user_order_summary
    
    # Any authenticated user can access this (authorization checks happen at frontend)
    summary = await get_user_order_summary(user_id)
    return summary


@router.put("/avatar")
async def update_avatar(
    avatar_data: AvatarUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user's avatar (base64 image)"""
    db = await get_database()
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not avatar_data.avatar:
        raise HTTPException(status_code=400, detail="Avatar image is required")
    
    # Update avatar
    result = await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"avatar": avatar_data.avatar}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Avatar updated successfully", "avatar": avatar_data.avatar}
