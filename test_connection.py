import motor.motor_asyncio
from dotenv import load_dotenv
import os
import asyncio
import urllib.parse
import certifi

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URL
    mongodb_url = os.getenv("MONGODB_URL")
    
    if not mongodb_url:
        print("Error: MONGODB_URL not found in environment variables")
        return
        
    try:
        # Create client with SSL certificate verification
        print("Attempting to connect to MongoDB...")
        print(f"Using URL: {mongodb_url.replace(mongodb_url.split('@')[0], '***')}")  # Hide credentials in log
        
        # Use certifi for SSL certificate verification
        client = motor.motor_asyncio.AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            tlsCAFile=certifi.where()  # Add SSL certificate verification
        )
        
        # Get database
        db = client.parentassistant
        
        # Test connection with simple operation
        print("Testing database operation...")
        await db.users.find_one({})
        
        print("Successfully connected to MongoDB!")
        
        # List all collections
        collections = await db.list_collection_names()
        print("Available collections:", collections)
        
    except Exception as e:
        print("Connection failed:", str(e))
        print("\nTroubleshooting steps:")
        print("1. Ensure certifi is installed:")
        print("   pip install certifi")
        print("2. Verify your connection string includes SSL parameters:")
        print("   ?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_REQUIRED")
        print("3. Check if your Python environment has access to root certificates")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
