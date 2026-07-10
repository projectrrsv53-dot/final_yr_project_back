
import asyncio

from database import db
from passwordhashing import hash_password

async def create_user():

    users = db.users

    hashed = hash_password("mypass")

    result = await users.insert_one({
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "password_hash": hashed,
        "role": "patient"
    })

    print("Inserted ID:", result.inserted_id)

asyncio.run(create_user())