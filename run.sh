#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if requirements are installed
if ! pip list | grep -q "fastapi"; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please update .env with your actual API keys"
fi

# Run the server
echo "Starting server..."
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
