"""
Script to update existing categories and mark Birds & Fishes as coming soon
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "epet_db"

async def update_categories():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    # Define categories with proper structure
    categories_data = [
        {
            "name": "Dogs",
            "description": "Products for dogs including food, toys, and accessories",
            "icon": "🐕",
            "coming_soon": False
        },
        {
            "name": "Cats",
            "description": "Products for cats including food, toys, and accessories",
            "icon": "🐱",
            "coming_soon": False
        },
        {
            "name": "Birds",
            "description": "Products for birds - Coming Soon!",
            "icon": "🦜",
            "coming_soon": True
        },
        {
            "name": "Fishes",
            "description": "Products for fishes - Coming Soon!",
            "icon": "🐠",
            "coming_soon": True
        }
    ]
    
    try:
        # Clear existing categories
        await db.categories.delete_many({})
        print("Cleared existing categories")
        
        # Insert new categories
        result = await db.categories.insert_many(categories_data)
        print(f"Inserted {len(result.inserted_ids)} categories")
        
        # Display inserted categories
        categories = await db.categories.find().to_list(100)
        print("\nCategories in database:")
        for cat in categories:
            print(f"  - {cat['name']} ({'Coming Soon' if cat.get('coming_soon') else 'Active'})")
        
        print("\n✅ Categories updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_categories())
