# Requirements

## Python Dependencies
- fastapi >= 0.104.0
- uvicorn[standard] >= 0.24.0
- motor >= 3.3.0 (async MongoDB driver)
- pydantic >= 2.5.0
- pydantic-settings >= 2.1.0
- python-dotenv >= 1.0.0

## Development Dependencies
- pytest >= 7.4.0
- pytest-asyncio >= 0.21.0
- httpx >= 0.25.0 (for testing)

## System Requirements
- Python 3.10+
- MongoDB 6.0+ (local installation)

## Setup Instructions
1. Ensure MongoDB is running: `sudo systemctl start mongodb`
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run: `uvicorn app.main:app --reload`