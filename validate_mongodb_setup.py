import os
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio
import certifi
from urllib.parse import urlparse, parse_qs

def analyze_connection_string(url):
    """Analyze MongoDB connection string without exposing credentials"""
    try:
        # Parse the URL
        parsed = urlparse(url)
        
        # Get query parameters
        params = parse_qs(parsed.query)
        
        print("\nConnection String Analysis:")
        print(f"Protocol: {parsed.scheme}")
        print(f"Host: {parsed.hostname}")
        print(f"Database: {parsed.path.lstrip('/')}")
        print("\nQuery Parameters:")
        for key, value in params.items():
            print(f"- {key}: {value[0]}")
            
        # Basic validation
        if parsed.scheme != "mongodb+srv":
            print("\n⚠️ Warning: URL scheme should be 'mongodb+srv'")
        
        if not parsed.path.lstrip('/'):
            print("\n⚠️ Warning: No database name specified in the connection string")
            
        required_params = ['retryWrites', 'w']
        for param in required_params:
            if param not in params:
                print(f"\n⚠️ Warning: Missing recommended parameter: {param}")
                
    except Exception as e:
        print(f"Error analyzing connection string: {str(e)}")

async def validate_mongodb_setup():
    print("MongoDB Setup Validator")
    print("----------------------")
    
    # Load environment variables
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    
    if not mongodb_url:
        print("❌ Error: MONGODB_URL not found in .env file")
        return
    
    # Analyze connection string
    analyze_connection_string(mongodb_url)
    
    try:
        print("\nAttempting connection...")
        
        # Create client with detailed options
        client = motor.motor_asyncio.AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where(),
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Test database connection
        db = client.parentassistant
        
        print("\nTesting authentication and database access...")
        await db.command("ping")
        print("✅ Successfully connected to MongoDB!")
        
        # Test database operations
        print("\nTesting database operations...")
        
        # Try to list collections
        collections = await db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Try to create a test collection
        if 'test_collection' not in collections:
            await db.create_collection('test_collection')
            print("✅ Successfully created test collection")
            
            # Clean up
            await db.drop_collection('test_collection')
            print("✅ Successfully cleaned up test collection")
        
    except Exception as e:
        print("\n❌ Connection failed!")
        print(f"Error: {str(e)}")
        
        if "bad auth" in str(e):
            print("\n🔍 Authentication Troubleshooting:")
            print("1. Verify MongoDB Atlas user:")
            print("   - Go to Atlas → Database Access")
            print("   - Check if your user exists and has correct permissions")
            print("   - Ensure user is assigned to the correct database")
            
            print("\n2. Check user credentials:")
            print("   - Username and password are case-sensitive")
            print("   - Special characters in password are properly URL encoded")
            
            print("\n3. Verify database name:")
            print("   - Database name in connection string matches your Atlas database")
            
            print("\n4. Connection string format:")
            print("   mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority")
            
            print("\nWould you like to try recreating the user? (Recommended)")
            print("1. Go to Atlas → Database Access")
            print("2. Delete existing user")
            print("3. Create new user with password (no special characters)")
            print("4. Set role to 'Atlas admin' (for testing)")
            print("5. Update .env with new credentials")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(validate_mongodb_setup())
