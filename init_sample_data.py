"""
Script to initialize sample data for PawStore
Run: python init_sample_data.py
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.auth import get_password_hash

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "epet_db"


async def init_sample_data():
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # 1. Create Admin User
        print("Creating admin user...")
        admin_user = {
            "username": "admin@epet.com",
            "email": "admin@epet.com",
            "full_name": "Admin User",
            "password_hash": get_password_hash("admin1234"),
            "role": "admin",
            "register_time": datetime.utcnow(),
            "last_login_time": None
        }
        await db.users.update_one(
            {"username": "admin@epet.com"},
            {"$set": admin_user},
            upsert=True
        )
        print("✓ Admin user created/updated")
        
        # 2. Create Sample Users
        print("\nCreating sample users...")
        sample_users = [
            {
                "username": "john.doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "password_hash": get_password_hash("password123"),
                "role": "user",
                "register_time": datetime.utcnow(),
                "last_login_time": None
            },
            {
                "username": "sara.ali",
                "email": "sara@example.com",
                "full_name": "Sara Ali",
                "password_hash": get_password_hash("password123"),
                "role": "user",
                "register_time": datetime.utcnow(),
                "last_login_time": None
            }
        ]
        
        for user in sample_users:
            await db.users.update_one(
                {"username": user["username"]},
                {"$set": user},
                upsert=True
            )
        print(f"✓ Created {len(sample_users)} sample users")
        
        # 3. Create Pet Types
        print("\nCreating pet types...")
        pet_types = [
            {"pet_type": "Dogs"},
            {"pet_type": "Cats"},
            {"pet_type": "Birds"},
            {"pet_type": "Fishes"}
        ]
        
        pet_ids = {}
        for pet in pet_types:
            result = await db.pets.update_one(
                {"pet_type": pet["pet_type"]},
                {"$set": pet},
                upsert=True
            )
            if result.upserted_id:
                pet_ids[pet["pet_type"]] = str(result.upserted_id)
            else:
                found_pet = await db.pets.find_one({"pet_type": pet["pet_type"]})
                pet_ids[pet["pet_type"]] = str(found_pet["_id"])
        
        print(f"✓ Created {len(pet_types)} pet types")
        
        # 4. Create Categories
        print("\nCreating categories...")
        categories = [
            {"type": "Dogs"},
            {"type": "Cats"},
            {"type": "Birds"},
            {"type": "Fishes"}
        ]
        
        category_ids = {}
        for category in categories:
            result = await db.categories.update_one(
                {"type": category["type"]},
                {"$set": category},
                upsert=True
            )
            if result.upserted_id:
                category_ids[category["type"]] = str(result.upserted_id)
            else:
                found_cat = await db.categories.find_one({"type": category["type"]})
                category_ids[category["type"]] = str(found_cat["_id"])
        
        print(f"✓ Created {len(categories)} categories")
        
        # 5. Create Subcategories
        print("\nCreating subcategories...")
        subcategories = [
            {"category_id": category_ids["Dogs"], "subtype_description": "Accessories"},
            {"category_id": category_ids["Dogs"], "subtype_description": "Toys"},
            {"category_id": category_ids["Dogs"], "subtype_description": "Food"},
            {"category_id": category_ids["Cats"], "subtype_description": "Accessories"},
            {"category_id": category_ids["Cats"], "subtype_description": "Toys"},
            {"category_id": category_ids["Cats"], "subtype_description": "Food"},
        ]
        
        subtype_ids = {}
        for idx, subtype in enumerate(subcategories):
            result = await db.subcategories.insert_one(subtype)
            key = f"{subtype['category_id']}_{subtype['subtype_description']}"
            subtype_ids[key] = str(result.inserted_id)
        
        print(f"✓ Created {len(subcategories)} subcategories")
        
        # 6. Create Sample Products (Inventory)
        print("\nCreating sample products...")
        dog_acc_subtype = subtype_ids[f"{category_ids['Dogs']}_Accessories"]
        dog_food_subtype = subtype_ids[f"{category_ids['Dogs']}_Food"]
        cat_acc_subtype = subtype_ids[f"{category_ids['Cats']}_Accessories"]
        cat_toy_subtype = subtype_ids[f"{category_ids['Cats']}_Toys"]
        
        products = [
            {
                "pet_id": pet_ids["Dogs"],
                "product_name": "Premium Dog Collar",
                "product_image": "https://via.placeholder.com/400x400?text=Dog+Collar",
                "price": 24.99,
                "stock": 12,
                "subtype_id": dog_acc_subtype,
                "discount": 29.0,
                "rating": 4.8,
                "num_reviews": 234,
                "status": "available",
                "visibility": True
            },
            {
                "pet_id": pet_ids["Dogs"],
                "product_name": "Organic Dog Food - 5kg",
                "product_image": "https://via.placeholder.com/400x400?text=Dog+Food",
                "price": 45.99,
                "stock": 15,
                "subtype_id": dog_food_subtype,
                "discount": 18.0,
                "rating": 4.9,
                "num_reviews": 567,
                "status": "available",
                "visibility": True
            },
            {
                "pet_id": pet_ids["Dogs"],
                "product_name": "Interactive Chew Toy",
                "product_image": "https://via.placeholder.com/400x400?text=Chew+Toy",
                "price": 15.99,
                "stock": 87,
                "subtype_id": dog_acc_subtype,
                "discount": 0.0,
                "rating": 4.6,
                "num_reviews": 189,
                "status": "available",
                "visibility": True
            },
            {
                "pet_id": pet_ids["Cats"],
                "product_name": "Cozy Cat Bed",
                "product_image": "https://via.placeholder.com/400x400?text=Cat+Bed",
                "price": 39.99,
                "stock": 9,
                "subtype_id": cat_acc_subtype,
                "discount": 0.0,
                "rating": 4.7,
                "num_reviews": 120,
                "status": "available",
                "visibility": True
            },
            {
                "pet_id": pet_ids["Cats"],
                "product_name": "Feather Wand Toy",
                "product_image": "https://via.placeholder.com/400x400?text=Feather+Toy",
                "price": 12.99,
                "stock": 48,
                "subtype_id": cat_toy_subtype,
                "discount": 0.0,
                "rating": 4.5,
                "num_reviews": 92,
                "status": "available",
                "visibility": True
            }
        ]
        
        for product in products:
            await db.inventory.update_one(
                {"product_name": product["product_name"]},
                {"$set": product},
                upsert=True
            )
        
        print(f"✓ Created {len(products)} sample products")
        
        print("\n" + "="*50)
        print("✓ Sample data initialization completed!")
        print("="*50)
        print("\nAdmin Credentials:")
        print("  Username: admin@epet.com")
        print("  Password: admin1234")
        print("\nSample Users:")
        print("  john.doe / password123")
        print("  sara.ali / password123")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(init_sample_data())
