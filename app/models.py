from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# User Models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str = "user"
    status: str = "active"

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8)


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    password_hash: str
    register_time: datetime
    last_login_time: Optional[datetime] = None
    status: str = "active"

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    id: str = Field(alias="_id")
    register_time: datetime
    last_login_time: Optional[datetime] = None
    status: str = "active"

    class Config:
        from_attributes = True
        populate_by_name = True


# Pet Models
class PetBase(BaseModel):
    pet_type: str

    class Config:
        from_attributes = True


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    pet_type: Optional[str] = None


class PetInDB(PetBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PetResponse(PetBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# User Pet Profile Models (User's own pets - like "My Pets")
class UserPetProfileBase(BaseModel):
    user_id: str
    pet_name: str
    pet_type: str  # Store pet type as string (dogs, cats, birds, fishes)
    breed: str
    age: str
    image_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class UserPetProfileCreate(BaseModel):
    pet_name: str
    pet_type: str  # Store pet type as string (dogs, cats, birds, fishes)
    breed: str
    age: str
    image_url: Optional[str] = None
    notes: Optional[str] = None


class UserPetProfileUpdate(BaseModel):
    pet_name: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None


class UserPetProfileInDB(UserPetProfileBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserPetProfileResponse(UserPetProfileBase):
    id: str = Field(alias="_id")
    username: Optional[str] = None  # Username of the pet owner

    class Config:
        from_attributes = True
        populate_by_name = True


# Category Models
class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None
    image_url: Optional[str] = None
    coming_soon: bool = False

    class Config:
        from_attributes = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    coming_soon: Optional[bool] = None


class CategoryInDB(CategoryBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CategoryResponse(CategoryBase):
    id: str = Field(alias="_id")
    subcategories: Optional[list] = []

    class Config:
        from_attributes = True
        populate_by_name = True


# Subcategory Models
class SubcategoryBase(BaseModel):
    name: str
    category_id: str

    class Config:
        from_attributes = True


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[str] = None


class SubcategoryResponse(SubcategoryBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# Inventory Models
class InventoryBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int = 0
    category_id: str
    subcategory_id: Optional[str] = None
    images: List[str] = []
    weight: Optional[str] = None
    brand: Optional[str] = None
    age_range: Optional[str] = None
    rating: Optional[float] = 0.0
    num_reviews: Optional[int] = 0
    discount: Optional[float] = 0.0
    is_visible: bool = True

    class Config:
        from_attributes = True


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None
    images: Optional[List[str]] = None
    weight: Optional[str] = None
    brand: Optional[str] = None
    age_range: Optional[str] = None
    rating: Optional[float] = None
    num_reviews: Optional[int] = None
    discount: Optional[float] = None
    is_visible: Optional[bool] = None


class InventoryInDB(InventoryBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class InventoryResponse(InventoryBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# Cart Models
class CartBase(BaseModel):
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    user_id: str


class CartInDB(CartBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CartResponse(CartBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# CartItem Models
class CartItemBase(BaseModel):
    inventory_id: str
    quantity: int = 1

    class Config:
        from_attributes = True


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartItemInDB(CartItemBase):
    id: str = Field(alias="_id")
    cart_id: str

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CartItemResponse(CartItemBase):
    id: str = Field(alias="_id")
    cart_id: str

    class Config:
        from_attributes = True
        populate_by_name = True


# Order Models
class OrderBase(BaseModel):
    user_id: str
    order_time: datetime = Field(default_factory=datetime.utcnow)
    payment_type: str = "cod"  # cod = Cash On Delivery
    status: str = "pending"
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: str
    city: str
    zip_code: str
    subtotal: float = 0.0
    delivery_charges: float = 0.0
    total: float = 0.0

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    payment_type: str = "cod"
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    zip_code: str


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_type: Optional[str] = None


class OrderInDB(OrderBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class OrderResponse(OrderBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


# OrderItem Models
class OrderItemBase(BaseModel):
    order_id: str
    inventory_id: str
    price: float
    quantity: int = 1
    product_name: Optional[str] = None
    product_image: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemInDB(OrderItemBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class OrderItemResponse(OrderItemBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# UserPet Models (Junction table)
class UserPetBase(BaseModel):
    user_id: str
    pet_id: str

    class Config:
        from_attributes = True


class UserPetCreate(UserPetBase):
    pass


class UserPetInDB(UserPetBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserPetResponse(UserPetBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# Wishlist Models
class WishlistItemBase(BaseModel):
    user_id: str
    inventory_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class WishlistItemCreate(BaseModel):
    inventory_id: str


class WishlistItemInDB(WishlistItemBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class WishlistItemResponse(WishlistItemBase):
    id: str = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


# Token Models
class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[dict] = None
    encrypted_response: Optional[str] = None  # For encrypted responses


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    encrypted: Optional[str] = None  # For encrypted credentials


# Dashboard Models
class DashboardStats(BaseModel):
    total_revenue: float
    total_orders: int
    pending_orders: int
    total_users: int
    active_users: int
    low_stock_items: int


class RecentOrder(BaseModel):
    order_id: str = Field(alias="_id")
    customer_name: str
    customer_email: str
    total: float
    status: str
    date: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
