import motor.motor_asyncio
from dotenv import load_dotenv
import os
import asyncio
import certifi

async def init_database():
    # Load environment variables
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    
    if not mongodb_url:
        print("Error: MONGODB_URL not found in environment variables")
        return
        
    try:
        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(
            mongodb_url,
            tlsCAFile=certifi.where()
        )
        
        # Get database
        db = client.parentassistant
        
        # Create collections if they don't exist
        collections = [
            "users",
            "threads",
            "messages",
            "responses",
            "user_profiles"
        ]
        
        existing_collections = await db.list_collection_names()
        
        for collection in collections:
            if collection not in existing_collections:
                await db.create_collection(collection)
                print(f"Created collection: {collection}")
        
        # Create indexes
        print("\nCreating indexes...")
        
        # Users collection
        await db.users.create_index("created_at")
        await db.users.create_index("last_login")
        print("Created indexes for users collection")
        
        # Threads collection
        await db.threads.create_index("user_id")
        await db.threads.create_index("thread_id")
        await db.threads.create_index("created_at")
        print("Created indexes for threads collection")
        
        # Messages collection
        await db.messages.create_index("thread_id")
        await db.messages.create_index("user_id")
        await db.messages.create_index("created_at")
        await db.messages.create_index("question_type")
        print("Created indexes for messages collection")
        
        # Responses collection
        await db.responses.create_index("thread_id")
        await db.responses.create_index("user_id")
        await db.responses.create_index("created_at")
        print("Created indexes for responses collection")
        
        # User profiles collection
        await db.user_profiles.create_index("user_id")
        await db.user_profiles.create_index("updated_at")
        print("Created indexes for user_profiles collection")
        
        print("\nDatabase initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(init_database())
