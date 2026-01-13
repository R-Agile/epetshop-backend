"""
Script to create a superuser (admin) for the PawStore application
Usage: python create_superuser.py
"""
import asyncio
from getpass import getpass
from app.database import connect_to_mongo, get_database
from app.auth import get_password_hash
from datetime import datetime


async def create_superuser():
    print("=" * 50)
    print("PawStore - Create Superuser")
    print("=" * 50)
    
    # Connect to database
    await connect_to_mongo()
    db = await get_database()
    
    # Get user input
    print("\nEnter superuser details:")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    full_name = input("Full Name: ").strip()
    password = getpass("Password: ")
    password_confirm = getpass("Confirm Password: ")
    
    # Validate input
    if not all([username, email, full_name, password]):
        print("\n❌ Error: All fields are required!")
        return
    
    if password != password_confirm:
        print("\n❌ Error: Passwords do not match!")
        return
    
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"email": email}, {"username": username}]})
    if existing_user:
        print(f"\n❌ Error: User with email '{email}' or username '{username}' already exists!")
        return
    
    # Create superuser
    user_dict = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password_hash": get_password_hash(password),
        "role": "super_user",  # Superuser role
        "register_time": datetime.utcnow(),
        "last_login_time": None
    }
    
    result = await db.users.insert_one(user_dict)
    
    print("\n" + "=" * 50)
    print("✅ Superuser created successfully!")
    print("=" * 50)
    print(f"User ID: {result.inserted_id}")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Role: super_user")
    print("\nYou can now login to the admin portal at: /admin/login")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(create_superuser())
