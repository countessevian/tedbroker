#!/bin/bash

# TED Broker FastAPI Server Startup Script

echo "Starting TED Broker FastAPI Server..."
echo "======================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run the application
echo "======================================="
echo "Starting server on http://0.0.0.0:8000"
echo "Press Ctrl+C to stop the server"
echo "======================================="
python main.py
