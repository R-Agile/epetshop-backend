"""
Script to add status field to existing users in the database
Run this once to update all existing users with default 'active' status
"""
import asyncio
from app.database import get_database


async def update_users_with_status():
    db = await get_database()
    
    # Update all users without a status field
    result = await db.users.update_many(
        {"status": {"$exists": False}},
        {"$set": {"status": "active"}}
    )
    
    print(f"Updated {result.modified_count} users with default 'active' status")
    
    # Show all users
    users = await db.users.find({}, {"username": 1, "email": 1, "status": 1}).to_list(100)
    print("\nCurrent users:")
    for user in users:
        print(f"  - {user['username']} ({user['email']}): {user.get('status', 'NO STATUS')}")


if __name__ == "__main__":
    asyncio.run(update_users_with_status())
