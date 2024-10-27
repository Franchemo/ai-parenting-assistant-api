# AI Parenting Assistant Backend API

This is the backend API service for the AI Parenting Assistant WeChat Mini Program. It handles communication between the Mini Program and OpenAI's API.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- OpenAI API key
- OpenAI Assistant ID

## Setup

1. Clone the repository and navigate to the backend_api directory:
```bash
cd backend_api
```

2. Create a virtual environment and activate it:
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
```

5. Edit the .env file with your actual credentials:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=your_assistant_id_here
```

## Running the Server

1. Start the server:
```bash
cd app
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check endpoint
- `POST /api/thread` - Create a new chat thread
- `POST /api/chat` - Send a message and get AI response
- `POST /api/clear` - Clear chat history

## Testing the API

You can test the API using the built-in Swagger documentation at `http://localhost:8000/docs`

## Deployment

For production deployment:

1. Set up a server (e.g., AWS EC2, DigitalOcean Droplet)
2. Install required dependencies
3. Set up a reverse proxy (e.g., Nginx)
4. Use a process manager (e.g., PM2, Supervisor)
5. Configure SSL certificates
6. Update CORS settings in main.py with your Mini Program's domain

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Notes

1. Never commit your .env file
2. Use HTTPS in production
3. Implement rate limiting
4. Add proper authentication for production use
5. Update CORS settings for production

## Integration with WeChat Mini Program

Update the BASE_URL in your Mini Program's api.js:

```javascript
// wechat_miniprogram/utils/api.js
const BASE_URL = 'https://your-api-domain.com/api';
```

## Support

For issues or questions, please create an issue in the repository.
