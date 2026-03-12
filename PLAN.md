# TED Broker - Project Specification & Implementation Plan

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Frontend Structure](#frontend-structure)
7. [Internationalization (i18n)](#internationalization-i18n)
8. [Security Features](#security-features)
9. [Authentication & Authorization](#authentication--authorization)
10. [Features & Modules](#features--modules)
11. [Configuration](#configuration)

---

## Project Overview

**TED Broker** is a web-based copy trading platform that allows users to:
- Register and authenticate (with 2FA)
- Browse and copy expert traders
- Invest in various plans (ETF, DeFi, Options)
- Manage wallets (deposits/withdrawals)
- Complete KYC onboarding
- Chat with support
- Receive notifications

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI (Python 3.x) |
| Database | MongoDB |
| Frontend | HTML/CSS/JS (Vanilla) |
| Authentication | JWT (JSON Web Tokens) |
| Password Hashing | Argon2 |
| Email Service | SendGrid |
| 2FA | TOTP-based |
| OAuth | Google OAuth 2.0 |
| Rate Limiting | SlowAPI |
| External APIs | Google OAuth, SendGrid, ipapi.co |

---

## Architecture

### Project Structure
```
tedbroker.com/
├── main.py                 # FastAPI application entry point
├── server.py               # Server runner script
├── requirements.txt        # Python dependencies
├── .env                   # Environment configuration
├── app/
│   ├── __init__.py
│   ├── auth.py            # Authentication utilities (JWT, password hashing)
│   ├── database.py        # MongoDB connection & collection definitions
│   ├── schemas.py         # Pydantic models (810 lines)
│   ├── email_service.py   # SendGrid email service (1241 lines)
│   ├── login_history.py  # Login tracking service
│   ├── referrals_service.py # Referral system
│   ├── security_alerts.py # Security alerts service
│   ├── twofa_service.py  # Two-factor authentication
│   ├── rate_limiter.py    # Rate limiting
│   └── routes/
│       ├── auth.py         # Authentication routes (1583 lines)
│       ├── admin.py        # Admin dashboard routes (112KB)
│       ├── traders.py      # Expert traders routes
│       ├── plans.py        # Investment plans
│       ├── etf_plans.py    # ETF investment plans
│       ├── defi_plans.py   # DeFi investment plans
│       ├── options_plans.py # Options trading plans
│       ├── wallet.py       # Wallet management
│       ├── deposits.py     # Deposit handling
│       ├── withdrawals.py  # Withdrawal handling
│       ├── investments.py  # User investments
│       ├── referrals.py    # Referral system routes
│       ├── news.py         # Market news
│       ├── crypto_wallets.py # Crypto wallet management
│       ├── chat.py         # Chat/messaging system
│       ├── onboarding.py   # KYC onboarding flow
│       ├── notifications.py # Notifications
│       └── language.py     # Language/i18n API
├── public/
│   └── copytradingbroker.io/  # Frontend HTML files
│       ├── index.html
│       ├── dashboard.html     # User dashboard (199KB)
│       ├── admin-dashboard.html
│       ├── login.html
│       ├── register.html
│       ├── onboarding.html
│       ├── traders.html
│       ├── about-us.html
│       ├── contact-us.html
│       ├── faqs.html
│       ├── investors.html
│       ├── how_it_works.html
│       ├── forgot-password.html
│       ├── verify-2fa.html
│       ├── reset-password.html
│       ├── privacy-policy.html
│       ├── legal/
│       │   ├── privacy_policy.html
│       │   ├── terms_conditions.html
│       │   ├── aml_policy.html
│       │   ├── risk_closure.html
│       │   └── index.html
│       ├── assets/
│       │   ├── js/
│       │   │   ├── dashboard.js        # Main dashboard logic (217KB)
│       │   │   ├── admin-dashboard.js  # Admin dashboard (129KB)
│       │   │   ├── language.js         # i18n system (270 lines)
│       │   │   ├── chat-widget.js      # Chat functionality
│       │   │   ├── onboarding.js       # KYC flow
│       │   │   ├── auth.js             # Authentication helpers
│       │   │   └── ...
│       │   ├── css/
│       │   ├── images/
│       │   └── translations/
│       │       ├── en.json, es.json, zh.json, hi.json
│       │       ├── fr.json, ar.json, bn.json, ru.json
│       │       ├── pt.json, de.json
│       └── uploads/
│           └── kyc/                   # KYC document uploads
└── docs/
    ├── API_DOCUMENTATION.md
    ├── RENDER_DEPLOYMENT.md
    ├── CLAUDE.md
    └── requirements.md
```

---

## Database Schema

### Collections

| Collection Name | Purpose |
|----------------|---------|
| `users` | User accounts |
| `expert_traders` | Copy trading experts |
| `investment_plans` | Standard investment plans |
| `etf_plans` | ETF investment options |
| `defi_plans` | DeFi portfolio options |
| `options_plans` | Options trading plans |
| `transactions` | Wallet transactions |
| `deposit_requests` | User deposits |
| `withdrawal_requests` | User withdrawals |
| `crypto_wallets` | Saved crypto addresses |
| `bank_accounts` | Saved bank accounts |
| `user_investments` | User investment records |
| `user_bank_accounts` | User bank account details |
| `user_crypto_addresses` | User crypto addresses |
| `chat_conversations` | Support chat threads |
| `chat_messages` | Chat messages |
| `notifications` | User notifications |

### User Schema (Core Fields)
```json
{
  "_id": "ObjectId",
  "email": "string",
  "username": "string",
  "hashed_password": "string",
  "full_name": "string",
  "phone": "string",
  "gender": "string",
  "country": "string",
  "account_types": ["string"],
  "wallet_balance": 0.0,
  "is_active": true,
  "is_verified": false,
  "two_fa_enabled": false,
  "auth_provider": "local",
  "google_id": "string",
  "profile_picture": "string",
  "selected_traders": ["trader_id"],
  "access_granted": false,
  "preferred_language": "en",
  "onboarding": {
    "first_name": "string",
    "last_name": "string",
    "gender": "string",
    "street": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "country": "string",
    "document_number": "string",
    "document_photo": "string",
    "personal_info_completed": false,
    "address_completed": false,
    "kyc_completed": false,
    "kyc_status": "pending_review"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/token` | OAuth2 token endpoint |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/change-password` | Change password |
| DELETE | `/api/auth/delete-account` | Delete account |
| POST | `/api/auth/verify-2fa` | Verify 2FA code |
| POST | `/api/auth/enable-2fa` | Enable 2FA |
| POST | `/api/auth/disable-2fa` | Disable 2FA |
| POST | `/api/auth/forgot-password` | Forgot password |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/google` | Google OAuth login |
| GET | `/api/auth/google/callback` | Google OAuth callback |

### Language (`/api/language`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/language/supported` | Get supported languages |
| GET | `/api/language/detect` | Detect language from IP |
| GET | `/api/language/preference` | Get user preference |
| PUT | `/api/language/preference` | Set user preference |

### Onboarding (`/api/onboarding`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/onboarding/status` | Get onboarding status |
| GET | `/api/onboarding/data` | Get onboarding data |
| POST | `/api/onboarding/personal-info` | Submit personal info |
| POST | `/api/onboarding/address` | Submit address |
| POST | `/api/onboarding/kyc` | Submit KYC documents |
| POST | `/api/onboarding/questionnaire` | Submit investment questionnaire |

### Traders (`/api/traders`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/traders` | List all traders |
| GET | `/api/traders/{id}` | Get trader details |
| POST | `/api/traders/{id}/copy` | Copy a trader |

### Investments (`/api/plans`, `/api/investments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plans` | List investment plans |
| GET | `/api/etf-plans` | List ETF plans |
| GET | `/api/defi-plans` | List DeFi plans |
| GET | `/api/options-plans` | List Options plans |
| POST | `/api/investments` | Create investment |
| GET | `/api/investments` | User investments |
| GET | `/api/investments/portfolio` | Portfolio summary |

### Wallet (`/api/wallet`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wallet/balance` | Get balance |
| GET | `/api/wallet/transactions` | Transaction history |

### Deposits (`/api/deposits`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/deposits` | Create deposit request |
| GET | `/api/deposits` | User deposits |
| GET | `/api/deposits/{id}` | Deposit details |

### Withdrawals (`/api/withdrawals`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/withdrawals` | Create withdrawal |
| GET | `/api/withdrawals` | User withdrawals |
| POST | `/api/withdrawals/{id}/verify` | Verify withdrawal |
| POST | `/api/withdrawals/{id}/cancel` | Cancel withdrawal |

### Bank Accounts (`/api/wallet/bank-accounts`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wallet/bank-accounts` | List bank accounts |
| POST | `/api/wallet/bank-accounts` | Add bank account |
| DELETE | `/api/wallet/bank-accounts/{id}` | Remove bank account |

### Crypto Addresses (`/api/wallet/crypto-addresses`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wallet/crypto-addresses` | List crypto addresses |
| POST | `/api/wallet/crypto-addresses` | Add crypto address |
| DELETE | `/api/wallet/crypto-addresses/{id}` | Remove crypto address |

### Chat (`/api/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/conversations` | List conversations |
| GET | `/api/chat/conversations/{id}` | Get conversation with messages |
| POST | `/api/chat/messages` | Send message |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | User notifications |
| PUT | `/api/notifications/{id}/dismiss` | Dismiss notification |
| POST | `/api/notifications/create` | Create notification (admin) |

### Referrals (`/api/referrals`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/referrals/my-code` | Get referral code |
| GET | `/api/referrals/stats` | Referral statistics |
| GET | `/api/referrals/referred-users` | Referred users |

### Admin (`/api/admin`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| PUT | `/api/admin/users/{id}/approve` | Approve user access |
| PUT | `/api/admin/users/{id}/suspend` | Suspend user |
| GET | `/api/admin/deposits` | All deposits |
| PUT | `/api/admin/deposits/{id}/approve` | Approve deposit |
| PUT | `/api/admin/deposits/{id}/reject` | Reject deposit |
| GET | `/api/admin/withdrawals` | All withdrawals |
| PUT | `/api/admin/withdrawals/{id}/approve` | Approve withdrawal |
| PUT | `/api/admin/withdrawals/{id}/reject` | Reject withdrawal |
| GET | `/api/admin/kyc` | KYC submissions |
| PUT | `/api/admin/kyc/{id}/approve` | Approve KYC |
| PUT | `/api/admin/kyc/{id}/reject` | Reject KYC |
| GET | `/api/admin/stats` | Platform statistics |

---

## Frontend Structure

### Pages
| Page | Route | Description |
|------|-------|-------------|
| Home | `/`, `/index` | Landing page |
| About | `/about-us` | Company information |
| Contact | `/contact-us` | Contact form |
| FAQs | `/faqs` | Frequently asked questions |
| Traders | `/traders` | Expert traders listing |
| Investors | `/investors` | Investor information |
| How It Works | `/how_it_works` | Platform explanation |
| Login | `/login` | User login |
| Register | `/register` | User registration |
| Forgot Password | `/forgot-password` | Password recovery |
| Verify 2FA | `/verify-2fa` | 2FA verification |
| Reset Password | `/reset-password` | Password reset |
| Dashboard | `/dashboard` | User dashboard (protected) |
| Onboarding | `/onboarding` | KYC wizard (protected) |
| Admin Login | `/admin/login` | Admin login |
| Admin Register | `/admin/register` | Admin registration |
| Admin Dashboard | `/admin/dashboard` | Admin panel (protected) |
| Privacy Policy | `/privacy-policy` | Privacy policy |
| Legal | `/legal/*` | Legal pages |

### Frontend JavaScript Modules
| File | Purpose |
|------|---------|
| `dashboard.js` | Main user dashboard functionality |
| `admin-dashboard.js` | Admin panel functionality |
| `language.js` | Internationalization system |
| `chat-widget.js` | Real-time chat support |
| `onboarding.js` | KYC document upload flow |
| `auth.js` | Authentication helpers |
| `login-handler.js` | Login form handling |
| `register-handler.js` | Registration form handling |
| `password-change.js` | Password management |
| `password-create.js` | OAuth password setup |
| `admin-chat.js` | Admin chat interface |

### CSS Framework
- Bootstrap 5 (via CDN)
- Custom CSS for theming
- RTL support for Arabic

---

## Internationalization (i18n)

### Supported Languages (10)
| Code | Language | Flag |
|------|----------|------|
| `en` | English | 🇺🇸 |
| `zh` | Chinese (中文) | 🇨🇳 |
| `hi` | Hindi (हिन्दी) | 🇮🇳 |
| `es` | Spanish (Español) | 🇪🇸 |
| `fr` | French (Français) | 🇫🇷 |
| `ar` | Arabic (العربية) | 🇸🇦 |
| `bn` | Bengali (বাংলা) | 🇧🇩 |
| `ru` | Russian (Русский) | 🇷🇺 |
| `pt` | Portuguese (Português) | 🇵🇹 |
| `de` | German (Deutsch) | 🇩🇪 |

### Translation System
- **Translation Files**: JSON files in `/assets/translations/`
- **Implementation**: `data-i18n` attributes in HTML elements
- **Language Detection**: IP-based detection via ipapi.co
- **Persistence**: localStorage + user preference in MongoDB
- **RTL Support**: Full RTL layout for Arabic
- **Language API**: `/api/language/*` endpoints

---

## Security Features

### Authentication
- JWT-based authentication with configurable expiration (default: 30 min)
- Argon2 password hashing
- Google OAuth 2.0 support
- Optional 2FA (TOTP via email)

### Rate Limiting
- SlowAPI-based rate limiting
- Configurable limits per endpoint

### Security Services
- Login history tracking
- Security alerts
- IP-based location detection

### Input Validation
- Pydantic models for all requests
- Email validation
- Password strength requirements (8+ chars, uppercase, lowercase, number)

### Admin Access Control
- Dashboard access requires admin approval (`access_granted` flag)
- Role-based access (user vs admin)

---

## Authentication & Authorization

### User Roles
| Role | Description |
|------|-------------|
| `user` | Standard registered user |
| `admin` | Platform administrator |

### Access Levels
1. **Public**: No authentication required
2. **Authenticated**: Valid JWT token required
3. **Dashboard Access**: `access_granted = true` required
4. **Admin**: Admin role required

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### Username Requirements
- 3-50 characters
- Only letters, numbers, hyphens, and underscores

---

## Features & Modules

### 1. User Registration & Authentication
- Email/password registration
- Google OAuth login
- 2FA verification via email
- Password reset flow

### 2. Copy Trading
- Browse expert traders
- View trader statistics (YTD return, win rate, copiers)
- Copy trade with minimum amounts

### 3. Investment Plans
- Standard investment plans
- ETF plans (Conservative, Moderate, Aggressive)
- DeFi plans (Conservative, Moderate, Aggressive, Balanced)
- Options plans (Beginner, Intermediate, Advanced, Expert)

### 4. Wallet Management
- View balance
- Transaction history
- Bank account management
- Crypto address management

### 5. Deposits & Withdrawals
- Deposit requests (bank transfer, crypto, card)
- Withdrawal requests (bank, crypto)
- 8-digit verification codes for withdrawals
- Admin approval workflow

### 6. Onboarding (KYC)
- Step 1: Personal Information
- Step 2: Address Information
- Step 3: KYC Document Upload
- Investment questionnaire

### 7. Chat Support
- User-admin messaging
- Conversation management
- Real-time chat widget

### 8. Notifications
- System notifications
- Admin-created notifications
- Notification dismissal

### 9. Referrals
- Unique referral codes
- Referral tracking
- Referral statistics

### 10. Internationalization
- 10 language support
- Auto language detection
- RTL support for Arabic

---

## Configuration

### Environment Variables

```env
# MongoDB
MONGODB_URL=mongodb+srv://...
DATABASE_NAME=tedbroker

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000

# SendGrid
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=accounts@tedbrokers.com
SENDGRID_FROM_NAME=TED Brokers

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# News APIs (Optional)
NEWSAPI_KEY=
FINNHUB_API_KEY=
ALPHAVANTAGE_API_KEY=
```

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Python
python main.py

# Run with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Implementation Status

### Completed Features
- [x] User registration & authentication
- [x] JWT authentication
- [x] 2FA via email
- [x] Google OAuth
- [x] Password reset flow
- [x] Copy trading system
- [x] Investment plans (Standard, ETF, DeFi, Options)
- [x] Wallet management
- [x] Deposits & withdrawals
- [x] Bank & crypto account management
- [x] KYC onboarding flow
- [x] Chat support system
- [x] Notifications
- [x] Referral system
- [x] Admin dashboard
- [x] Internationalization (10 languages)
- [x] Rate limiting

### Database Collections Created
- users
- expert_traders
- investment_plans
- etf_plans
- defi_plans
- options_plans
- transactions
- deposit_requests
- withdrawal_requests
- crypto_wallets
- bank_accounts
- user_investments
- user_bank_accounts
- user_crypto_addresses
- chat_conversations
- chat_messages
- notifications

---

*Last Updated: January 2026*
