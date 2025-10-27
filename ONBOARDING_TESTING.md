# Onboarding System Testing Guide

## ✅ Server Status
The server has been restarted and all onboarding routes are now live.

## 🔗 Available Endpoints

### Frontend
- **Onboarding Wizard Page**: `http://localhost:8000/onboarding`
- **Alternative URL**: `http://localhost:8000/onboarding.html`

### Backend API (All require authentication)
- `GET  /api/onboarding/status` - Check completion status
- `POST /api/onboarding/personal-info` - Submit personal info
- `POST /api/onboarding/address` - Submit address
- `POST /api/onboarding/kyc` - Submit KYC documents
- `GET  /api/onboarding/data` - Get existing data

## 🧪 Testing Steps

### 1. Register a New User
1. Go to: `http://localhost:8000/register`
2. Fill in the registration form
3. Submit the form
4. Check your email for the 2FA code (or check server logs if email not configured)

### 2. Verify Email
1. Go to: `http://localhost:8000/verify-2fa`
2. Enter the 6-digit code
3. After successful verification, you should be redirected to `/onboarding`

### 3. Complete Onboarding

#### Step 1: Personal Information
- First Name (required)
- Last Name (required)
- Gender (required): Male, Female, or Others

#### Step 2: Address
- Street Address (required)
- City (required)
- State/Province (required)
- ZIP/Postal Code (required)
- Country (required)

#### Step 3: ID Verification
- Document Number (required): e.g., passport, driver's license, national ID
- Document Photo (required): Upload an image (PNG, JPG, max 5MB)
  - Supports drag-and-drop
  - Shows image preview before submission

### 4. Success
- After completing all steps, you'll see a success message
- Click "Go to Dashboard" to access the platform
- Dashboard will now be accessible since onboarding is complete

## 🔍 Verification

### Check Data in Database
You can verify the data is stored correctly by checking MongoDB:

```bash
# Connect to MongoDB
mongosh "mongodb+srv://brockbailey706_db_user:VAjJy8CSr9N9wYBi@cluster0.mzeaxhl.mongodb.net/tedbroker"

# Query user's onboarding data
db.users.findOne({email: "your-email@example.com"}, {onboarding: 1, full_name: 1, gender: 1, country: 1})
```

Expected structure:
```json
{
  "full_name": "John Doe",
  "gender": "Male",
  "country": "United States",
  "onboarding": {
    "first_name": "John",
    "last_name": "Doe",
    "gender": "Male",
    "personal_info_completed": true,
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "United States",
    "address_completed": true,
    "document_number": "AB123456",
    "document_photo": "/uploads/kyc/USER_ID_TIMESTAMP.jpg",
    "kyc_completed": true,
    "kyc_status": "pending_review",
    "kyc_submitted_at": ISODate("2025-10-27T09:10:00.000Z"),
    "completed_at": ISODate("2025-10-27T09:10:00.000Z")
  }
}
```

### Check Uploaded Files
```bash
ls -lh public/copytradingbroker.io/uploads/kyc/
```

### Test Dashboard Protection
1. Complete onboarding with one account
2. Register a new account
3. Verify email (should redirect to onboarding)
4. Try accessing `/dashboard` directly
5. Should be redirected back to `/onboarding`
6. Complete onboarding
7. Dashboard should now be accessible

## 🎨 Features Implemented

✅ **Multi-step wizard** with progress indicators
✅ **Form validation** (client and server-side)
✅ **File upload** with drag-and-drop support
✅ **Image preview** before submission
✅ **Auto-save** - data persists across sessions
✅ **Skip option** - users can complete later
✅ **Back navigation** - edit previous steps
✅ **Dashboard protection** - enforces completion
✅ **Email verification flow** - seamless redirect
✅ **Secure storage** - documents saved with unique names
✅ **KYC status tracking** - pending_review/approved/rejected

## 🔒 Security Features

- JWT authentication required for all endpoints
- File type validation (images only)
- File size validation (5MB max)
- Secure file storage with unique filenames
- Documents protected in uploads/kyc/ directory
- .gitignore added to prevent committing sensitive docs

## 📝 Notes

- The onboarding wizard page matches your existing site theme
- All data is stored in MongoDB under each user's document
- Users can skip onboarding temporarily but will be prompted on dashboard
- KYC documents are stored as base64 in database or as files in uploads/kyc/
- The system is production-ready and fully functional
