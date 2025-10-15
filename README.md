# TED Broker Website

FastAPI application serving the TED Broker website.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Using Python directly:
```bash
python main.py
```

### Using Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at `http://localhost:8000`

## Available Routes

### Main Pages
- `/` or `/index` - Home page
- `/about-us` - About us page
- `/contact-us` - Contact us page
- `/faqs` - FAQs page
- `/investors` - Investors page
- `/traders` - Traders page
- `/how_it_works` - How it works page

### Authentication Pages
- `/register` - Registration page
- `/login` - Login page
- `/forgot-password` - Forgot password page

### Legal Pages
- `/privacy-policy` - Privacy policy page
- `/legal/privacy_policy` - Legal privacy policy
- `/legal/terms_conditions` - Terms and conditions
- `/legal/aml_policy` - AML policy
- `/legal/risk_closure` - Risk closure
- `/legal` - Legal index

### Static Assets
All static files (CSS, JS, images) are served from:
- `/assets/*` - All website assets
- `/temp/*` - Temporary files

## API Documentation

Once running, visit:
- `http://localhost:8000/docs` - Swagger UI documentation
- `http://localhost:8000/redoc` - ReDoc documentation
