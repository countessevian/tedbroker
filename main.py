from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, traders, plans, wallet, referrals, admin, deposits, investments, news, crypto_wallets, withdrawals, chat, onboarding
from app.rate_limiter import limiter

app = FastAPI(
    title="TED Broker API",
    description="RESTful API for TED Broker with authentication",
    version="1.0.0"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router)
# Include traders routes
app.include_router(traders.router)
# Include investment plans routes
app.include_router(plans.router)
# Include wallet routes
app.include_router(wallet.router)
# Include referrals routes
app.include_router(referrals.router)
# Include admin routes
app.include_router(admin.router)
# Include deposits routes
app.include_router(deposits.router)
# Include investments routes
app.include_router(investments.router)
# Include news routes
app.include_router(news.router)
# Include crypto wallets routes
app.include_router(crypto_wallets.router)
# Include withdrawals routes
app.include_router(withdrawals.router)
# Include chat routes
app.include_router(chat.router)
# Include onboarding routes
app.include_router(onboarding.router)


@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    close_mongo_connection()

# Get the base directory - current folder is the root
BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR  # Use current directory as site root

# Check if we have a public/copytradingbroker.io subdirectory and use it
if (BASE_DIR / "public" / "copytradingbroker.io").exists():
    SITE_DIR = BASE_DIR / "public" / "copytradingbroker.io"
# Otherwise check for public directory
elif (BASE_DIR / "public").exists():
    SITE_DIR = BASE_DIR / "public"

# Mount static files for assets (CSS, JS, images, etc)
if (SITE_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(SITE_DIR / "assets")), name="assets")

if (SITE_DIR / "temp").exists():
    app.mount("/temp", StaticFiles(directory=str(SITE_DIR / "temp")), name="temp")

if (SITE_DIR / "uploads").exists():
    app.mount("/uploads", StaticFiles(directory=str(SITE_DIR / "uploads")), name="uploads")

# Handle translate.google.com assets
if (SITE_DIR / "translate.google.com").exists():
    app.mount("/translate.google.com", StaticFiles(directory=str(SITE_DIR / "translate.google.com")), name="translate")


def read_html_file(file_path: Path) -> str:
    """Read and return HTML file content"""
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Page not found")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the home page"""
    return read_html_file(SITE_DIR / "index.html")


@app.get("/index", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def index():
    """Serve the index page"""
    return read_html_file(SITE_DIR / "index.html")


@app.get("/about-us", response_class=HTMLResponse)
@app.get("/about-us.html", response_class=HTMLResponse)
async def about_us():
    """Serve the about us page"""
    return read_html_file(SITE_DIR / "about-us.html")


@app.get("/contact-us", response_class=HTMLResponse)
@app.get("/contact-us.html", response_class=HTMLResponse)
async def contact_us():
    """Serve the contact us page"""
    return read_html_file(SITE_DIR / "contact-us.html")


@app.get("/faqs", response_class=HTMLResponse)
@app.get("/faqs.html", response_class=HTMLResponse)
async def faqs():
    """Serve the FAQs page"""
    return read_html_file(SITE_DIR / "faqs.html")


@app.get("/investors", response_class=HTMLResponse)
@app.get("/investors.html", response_class=HTMLResponse)
async def investors():
    """Serve the investors page"""
    return read_html_file(SITE_DIR / "investors.html")


@app.get("/traders", response_class=HTMLResponse)
@app.get("/traders.html", response_class=HTMLResponse)
async def traders():
    """Serve the traders page"""
    return read_html_file(SITE_DIR / "traders.html")


@app.get("/how_it_works", response_class=HTMLResponse)
@app.get("/how_it_works.html", response_class=HTMLResponse)
async def how_it_works():
    """Serve the how it works page"""
    return read_html_file(SITE_DIR / "how_it_works.html")


@app.get("/register", response_class=HTMLResponse)
@app.get("/register.html", response_class=HTMLResponse)
async def register():
    """Serve the register page"""
    return read_html_file(SITE_DIR / "register.html")


@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
async def login():
    """Serve the login page"""
    return read_html_file(SITE_DIR / "login.html")


@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page"""
    return read_html_file(SITE_DIR / "dashboard.html")


@app.get("/forgot-password", response_class=HTMLResponse)
@app.get("/forgot-password.html", response_class=HTMLResponse)
async def forgot_password():
    """Serve the forgot password page"""
    return read_html_file(SITE_DIR / "forgot-password.html")


@app.get("/verify-2fa", response_class=HTMLResponse)
@app.get("/verify-2fa.html", response_class=HTMLResponse)
async def verify_2fa_page():
    """Serve the 2FA verification page"""
    return read_html_file(SITE_DIR / "verify-2fa.html")


@app.get("/onboarding", response_class=HTMLResponse)
@app.get("/onboarding.html", response_class=HTMLResponse)
async def onboarding_page():
    """Serve the onboarding wizard page"""
    return read_html_file(SITE_DIR / "onboarding.html")


@app.get("/privacy-policy", response_class=HTMLResponse)
@app.get("/privacy-policy.html", response_class=HTMLResponse)
async def privacy_policy():
    """Serve the privacy policy page"""
    return read_html_file(SITE_DIR / "privacy-policy.html")


# Legal pages
@app.get("/legal/privacy_policy", response_class=HTMLResponse)
@app.get("/legal/privacy_policy.html", response_class=HTMLResponse)
async def legal_privacy_policy():
    """Serve the legal privacy policy page"""
    return read_html_file(SITE_DIR / "legal" / "privacy_policy.html")


@app.get("/legal/terms_conditions", response_class=HTMLResponse)
@app.get("/legal/terms_conditions.html", response_class=HTMLResponse)
async def legal_terms_conditions():
    """Serve the legal terms and conditions page"""
    return read_html_file(SITE_DIR / "legal" / "terms_conditions.html")


@app.get("/legal/aml_policy", response_class=HTMLResponse)
@app.get("/legal/aml_policy.html", response_class=HTMLResponse)
async def legal_aml_policy():
    """Serve the legal AML policy page"""
    return read_html_file(SITE_DIR / "legal" / "aml_policy.html")


@app.get("/legal/risk_closure", response_class=HTMLResponse)
@app.get("/legal/risk_closure.html", response_class=HTMLResponse)
async def legal_risk_closure():
    """Serve the legal risk closure page"""
    return read_html_file(SITE_DIR / "legal" / "risk_closure.html")


@app.get("/legal", response_class=HTMLResponse)
@app.get("/legal/", response_class=HTMLResponse)
@app.get("/legal/index", response_class=HTMLResponse)
@app.get("/legal/index.html", response_class=HTMLResponse)
async def legal_index():
    """Serve the legal index page"""
    return read_html_file(SITE_DIR / "legal" / "index.html")


# Admin pages
@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/", response_class=HTMLResponse)
@app.get("/admin/login", response_class=HTMLResponse)
@app.get("/admin/login.html", response_class=HTMLResponse)
async def admin_login_page():
    """Serve the admin login page"""
    return read_html_file(SITE_DIR / "admin-login.html")


@app.get("/admin/register", response_class=HTMLResponse)
@app.get("/admin/register.html", response_class=HTMLResponse)
async def admin_register_page():
    """Serve the admin registration page"""
    return read_html_file(SITE_DIR / "admin-register.html")


@app.get("/admin/dashboard", response_class=HTMLResponse)
@app.get("/admin/dashboard.html", response_class=HTMLResponse)
async def admin_dashboard_page():
    """Serve the admin dashboard page"""
    return read_html_file(SITE_DIR / "admin-dashboard.html")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
