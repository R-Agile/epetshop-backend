"""Quick script to create a test admin user"""
import asyncio
import sys
sys.path.insert(0, 'c:\\Users\\Laptop Zone by JK\\Desktop\\pawstore\\epet-backend')

from app.database import connect_to_mongo, get_database
from app.auth import get_password_hash
from datetime import datetime

async def main():
    await connect_to_mongo()
    db = await get_database()
    
    # Check if user exists
    existing = await db.users.find_one({'email': 'admin@pawstore.com'})
    if existing:
        print('Admin user already exists')
        return
    
    # Create admin user
    user_dict = {
        'username': 'admin',
        'email': 'admin@pawstore.com',
        'full_name': 'Admin User',
        'password_hash': get_password_hash('admin123'),
        'role': 'super_user',
        'created_at': datetime.utcnow(),
        'last_login_time': None
    }
    
    result = await db.users.insert_one(user_dict)
    print(f'✅ Admin user created successfully!')
    print(f'Email: admin@pawstore.com')
    print(f'Password: admin123')
    print(f'User ID: {result.inserted_id}')

if __name__ == '__main__':
    asyncio.run(main())
