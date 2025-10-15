# FastAPI MongoDB Application

## Project Overview
A RESTful API built with FastAPI and MongoDB for an online copy trading platform.

## Architecture
- **Backend**: FastAPI (Python 3.x)
- **Database**: MongoDB (local instance)
- **Environment**: Kali Linux, VSCode

## Project Structure
project/
├── app/
│   ├── main.py           # FastAPI application entry point
│   ├── models/           # Pydantic models
│   ├── routes/           # API route handlers
│   ├── database.py       # MongoDB connection
│   └── config.py         # Configuration settings
├── tests/
├── docs/
└── requirements.txt

## Key Conventions
- Use async/await for all database operations
- Follow RESTful API design principles
- Use Pydantic models for request/response validation
- Environment variables for configuration (use python-dotenv)
- Error handling with FastAPI's HTTPException

## MongoDB Setup
- Local MongoDB instance running on default port (27017)
- Database name: [your_db_name]
- Collections: [list your collections]

## Development Guidelines
- Use type hints throughout
- Follow PEP 8 style guide
- Include docstrings for all functions/classes
- Write tests for all endpoints