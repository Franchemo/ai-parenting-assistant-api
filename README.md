# AI Parenting Assistant Backend

## Detailed MongoDB Connection Steps

### 1. Create MongoDB Atlas Account and Cluster
1. Go to MongoDB Atlas (https://www.mongodb.com/cloud/atlas)
2. Sign up or log in
3. Create a new project (if needed)
4. Build a database:
   - Choose "FREE" shared cluster
   - Select cloud provider & region
   - Choose M0 Sandbox (Free)
   - Name your cluster (e.g., "ParentAssistant")

### 2. Set Up Database Access
1. In the left sidebar, click "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Enter username and password
   - Username: e.g., "parentassistant_admin"
   - Password: Generate a secure password
5. Set database user privileges:
   - Choose "Built-in Role"
   - Select "Atlas admin" for development (restrict for production)
6. Click "Add User"

### 3. Configure Network Access
1. In the left sidebar, click "Network Access"
2. Click "Add IP Address"
3. For development:
   - Click "Allow Access from Anywhere"
   - Click "Confirm"
4. For production:
   - Add specific IP addresses for Railway deployment (what does this mean)

### 4. Get Connection String
1. Go back to "Database" in sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Python" as your driver and "3.12 or later"
5. Copy the connection string:
   ```
   mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   ```
    
### 5. Set Up Environment Variables
1. Create/edit `.env` file in backend_api folder:
   ```
   MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/parentassistant?retryWrites=true&w=majority
   ```
   Replace:
   - `<username>` with your database username
   - `<password>` with your database password
   - `<cluster>` will already be filled with your cluster name

2. For Railway deployment:
   - Go to Railway dashboard
   - Select your project
   - Go to "Variables"
   - Add MONGODB_URL with the same connection string

### 6. Initialize Database Collections
1. In MongoDB Atlas:
   - Click "Browse Collections"
   - Click "Create Database"
   - Database name: "parentassistant"
   - Collection name: "users"
   - Click "Create"

2. Create remaining collections:
   - Click "Create Collection"
   - Add: "threads"
   - Add: "messages"
   - Add: "responses"
   - Add: "user_profiles"

### 7. Create Indexes
1. In MongoDB Atlas Shell or Compass, run these commands:
```javascript
// Users collection
db.users.createIndex({ "created_at": 1 });
db.users.createIndex({ "last_login": 1 });

// Threads collection
db.threads.createIndex({ "user_id": 1 });
db.threads.createIndex({ "thread_id": 1 });
db.threads.createIndex({ "created_at": 1 });

// Messages collection
db.messages.createIndex({ "thread_id": 1 });
db.messages.createIndex({ "user_id": 1 });
db.messages.createIndex({ "created_at": 1 });
db.messages.createIndex({ "question_type": 1 });

// Responses collection
db.responses.createIndex({ "thread_id": 1 });
db.responses.createIndex({ "user_id": 1 });
db.responses.createIndex({ "created_at": 1 });

// User profiles collection
db.user_profiles.createIndex({ "user_id": 1 });
db.user_profiles.createIndex({ "updated_at": 1 });
```

### 8. Verify Connection
1. Run this test script to verify connection:
```python
import motor.motor_asyncio
from dotenv import load_dotenv
import os
import asyncio

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URL
    mongodb_url = os.getenv("MONGODB_URL")
    
    try:
        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        
        # Get database
        db = client.parentassistant
        
        # Test connection with simple operation
        await db.users.find_one({})
        
        print("Successfully connected to MongoDB!")
        
        # List all collections
        collections = await db.list_collection_names()
        print("Available collections:", collections)
        
    except Exception as e:
        print("Connection failed:", str(e))
    
    finally:
        client.close()

# Run the test
asyncio.run(test_connection())
```

### 9. Database Schema

#### users Collection
```json
{
  "_id": ObjectId,
  "wechat_info": {
    "nickName": "string",
    "avatarUrl": "string",
    "gender": number,
    "country": "string",
    "province": "string",
    "city": "string",
    "language": "string"
  },
  "created_at": DateTime,
  "last_login": DateTime
}
```

#### threads Collection
```json
{
  "_id": ObjectId,
  "thread_id": "string",
  "user_id": "string",
  "created_at": DateTime
}
```

#### messages Collection
```json
{
  "_id": ObjectId,
  "thread_id": "string",
  "user_id": "string",
  "message": "string",
  "user_info": {
    "childAge": "string",
    "childPersonality": "string",
    "kindergarten": "string",
    "interests": "string",
    "languages": "string",
    "familyMembers": number,
    "hasSiblings": "string",
    "siblingsAge": "string"
  },
  "question_type": "string",
  "subcategory": "string",
  "created_at": DateTime
}
```

#### responses Collection
```json
{
  "_id": ObjectId,
  "thread_id": "string",
  "user_id": "string",
  "message": "string",
  "created_at": DateTime
}
```

#### user_profiles Collection
```json
{
  "_id": ObjectId,
  "user_id": "string",
  "child_info": {
    "age": "string",
    "personality": "string",
    "kindergarten": "string",
    "interests": "string",
    "languages": "string",
    "familyMembers": number,
    "hasSiblings": "string",
    "siblingsAge": "string"
  },
  "updated_at": DateTime
}
```

### 10. Monitoring Setup
1. In MongoDB Atlas:
   - Go to "Monitoring" in sidebar
   - Set up alerts:
     - Database metrics
     - Connection alerts
     - Performance alerts
2. Configure email notifications for alerts
（免费版可能没有）

### 11. Backup Configuration
1. In MongoDB Atlas:
   - Go to "Backup" in sidebar
   - Enable continuous backup
   - Set retention period (7 days recommended)
   - Configure point-in-time recovery
   - Set up scheduled snapshots

### 12. Best Practices
1. Connection Management:
   - Use connection pooling
   - Implement retry logic
   - Handle connection timeouts
2. Security:
   - Regularly rotate database credentials
   - Use least privilege access
   - Monitor access logs
3. Performance:
   - Use appropriate indexes
   - Monitor query performance
   - Implement caching where appropriate
