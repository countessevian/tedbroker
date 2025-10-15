# TED Broker API Documentation

## Overview

TED Broker provides a robust RESTful API for user registration and authentication using FastAPI, MongoDB, and JWT tokens.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in, you'll receive an access token that should be included in the Authorization header for protected routes.

### Header Format
```
Authorization: Bearer <your_access_token>
```

---

## API Endpoints

### 1. User Registration

Register a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123",
  "full_name": "John Doe" // optional
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Username Requirements:**
- 3-50 characters
- Only letters, numbers, hyphens, and underscores

**Success Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-14T02:40:53.408744",
  "updated_at": "2025-10-14T02:40:53.408748"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered or username taken
- `422 Unprocessable Entity`: Invalid input data

---

### 2. User Login

Login with email and password to receive an access token.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password
- `403 Forbidden`: User account is inactive

---

### 3. OAuth2 Token Login

OAuth2-compatible token endpoint (for Swagger UI and other OAuth2 clients).

**Endpoint:** `POST /api/auth/token`

**Request Body (Form Data):**
```
username: user@example.com  // Note: Use email in username field
password: SecurePassword123
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 4. Get Current User

Get the currently authenticated user's information.

**Endpoint:** `GET /api/auth/me`

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-14T02:40:53.408744",
  "updated_at": "2025-10-14T02:40:53.408748"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: User not found

---

### 5. Change Password

Change the current user's password.

**Endpoint:** `POST /api/auth/change-password`

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "old_password": "OldPassword123",
  "new_password": "NewSecurePassword456"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Incorrect old password
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: User not found

---

### 6. Delete Account

Delete the currently authenticated user's account.

**Endpoint:** `DELETE /api/auth/delete-account`

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "message": "Account deleted successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: User not found

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

---

## Testing

### Interactive API Documentation

Visit these URLs when the server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Test Script

Run the included test script:

```bash
python test_api.py
```

### Example cURL Commands

**Register:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

**Get Current User:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Security Features

1. **Password Hashing:** Argon2 algorithm for secure password storage
2. **JWT Tokens:** Signed tokens with expiration (30 minutes default)
3. **Input Validation:** Pydantic schemas for robust validation
4. **CORS:** Configurable Cross-Origin Resource Sharing
5. **Rate Limiting:** Can be added using FastAPI middleware

---

## Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "email": "user@example.com",
  "username": "johndoe",
  "hashed_password": "$argon2id$v=19$m=65536...",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": ISODate("2025-10-14T02:40:53.408Z"),
  "updated_at": ISODate("2025-10-14T02:40:53.408Z")
}
```

### Indexes

Recommended indexes for optimal performance:

```javascript
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })
```

---

## Configuration

Configure the API using environment variables in `.env`:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=tedbroker

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

---

## Production Deployment Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set secure CORS origins (replace `*` with specific domains)
- [ ] Enable HTTPS
- [ ] Set up proper MongoDB authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Enable database backups
- [ ] Configure proper error handling
- [ ] Set up health check endpoints
- [ ] Use environment-specific configuration

---

## Support

For issues or questions, please contact the development team or refer to the README.md file.
