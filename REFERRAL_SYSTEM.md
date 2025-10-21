# Referral System Documentation

## Overview

The TED Brokers referral system allows users to refer friends and earn rewards. When a new user signs up using a referral code, the referrer receives a bonus credited directly to their wallet.

## Features

### 1. **Unique Referral Links**
- Each user gets a unique 8-character referral code (e.g., `ABC12XYZ`)
- Referral codes are automatically generated when first accessed
- Full referral link format: `https://tedbrokers.com/register?ref=ABC12XYZ`

### 2. **New User Referral Modal**
- When a new user navigates to the dashboard for the first time, they see a welcome modal
- The modal prompts them to enter a referral code if they were referred
- Users can skip this step if they don't have a referral code
- The modal only appears once per user

### 3. **Referral Dashboard Tab**
- Dedicated "Referrals" tab in the user dashboard sidebar
- Displays:
  - User's unique referral link with copy-to-clipboard functionality
  - Total referrals count
  - Total earnings from referrals
  - Number of active referrals
  - Detailed list of all referred users with:
    - Username and email
    - Join date
    - Bonus earned
    - Status (completed/pending)

### 4. **Automatic Wallet Crediting**
- When a valid referral code is submitted:
  - System finds the referrer by their unique code
  - Credits the referrer's wallet with the base bonus amount ($50)
  - Creates a referral record in the database
  - Marks the new user as "referred by" the referrer

## Configuration

### Base Referral Bonus

The referral bonus amount is configured as a global variable in `app/referrals_service.py`:

```python
BASE_REFERRAL_BONUS = 50.0  # $50 bonus for each successful referral
```

To change the bonus amount, simply modify this value and restart the server.

## API Endpoints

### 1. Get Referral Link
**Endpoint:** `GET /api/referrals/my-link`
**Authentication:** Required (JWT token)
**Description:** Get the current user's referral link and code

**Response:**
```json
{
  "referral_link": "https://tedbrokers.com/register?ref=ABC12XYZ",
  "referral_code": "ABC12XYZ",
  "base_bonus": 50.0
}
```

### 2. Get Referral Statistics
**Endpoint:** `GET /api/referrals/my-statistics`
**Authentication:** Required (JWT token)
**Description:** Get detailed referral statistics for the current user

**Response:**
```json
{
  "total_referrals": 5,
  "total_earnings": 250.0,
  "active_referrals": 4,
  "base_bonus_amount": 50.0,
  "referred_users": [
    {
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "joined_date": "2025-10-20T12:30:00Z",
      "bonus_earned": 50.0,
      "status": "completed"
    }
  ]
}
```

### 3. Submit Referral Code
**Endpoint:** `POST /api/referrals/submit`
**Authentication:** Required (JWT token)
**Description:** Submit a referral code (used by new users)

**Request Body:**
```json
{
  "referral_code": "ABC12XYZ"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Referral bonus of $50.0 credited to referrer's wallet",
  "bonus_amount": 50.0
}
```

**Error Responses:**
- `400 Bad Request` - Invalid referral code
- `400 Bad Request` - User trying to refer themselves
- `400 Bad Request` - User already referred by someone else

### 4. Get Referral Configuration
**Endpoint:** `GET /api/referrals/config`
**Authentication:** None (public endpoint)
**Description:** Get referral system configuration

**Response:**
```json
{
  "base_referral_bonus": 50.0,
  "currency": "USD"
}
```

## Database Collections

### 1. Users Collection
**Collection Name:** `users`

**New Fields:**
- `referral_code` (string): Unique 8-character referral code
- `referred_by` (string): User ID of the person who referred this user

### 2. Referrals Collection
**Collection Name:** `referrals`

**Schema:**
```python
{
  "referrer_id": str,           # User ID of the referrer
  "referred_user_id": str,      # User ID of the referred user
  "referral_code": str,         # Referral code used
  "bonus_amount": float,        # Amount credited to referrer
  "status": str,                # "completed" or "pending"
  "created_at": datetime        # When the referral was made
}
```

## User Flow

### For Referrers:

1. User logs into dashboard
2. Clicks on "Referrals" tab in sidebar
3. System automatically generates a unique referral code if they don't have one
4. User copies their referral link
5. Shares link with friends via email, social media, etc.
6. When someone uses their link:
   - They see the referred user appear in their referrals list
   - Their wallet is automatically credited with $50
   - They can see earnings update in real-time

### For New Users (Referred):

1. User clicks on a referral link (e.g., `https://tedbrokers.com/register?ref=ABC12XYZ`)
2. Completes registration and 2FA verification
3. Logs into dashboard for the first time
4. Sees a welcome modal asking for referral code
5. The referral code from the URL is pre-filled (if they came from a referral link)
6. Submits the code:
   - System validates the code
   - Credits the referrer's wallet
   - Shows success message
   - User can now start investing

## Validation Rules

### Referral Code Validation:
- Must be exactly 8 characters long
- Contains only uppercase letters and digits
- Must be unique across all users
- Cannot be changed once generated

### Referral Submission Rules:
- Users cannot refer themselves
- Each user can only be referred once
- Referral code must exist in the system
- New users have one chance to submit a referral code

## Security Features

### Preventing Abuse:

1. **One-Time Submission:** Users can only submit a referral code once
2. **Self-Referral Prevention:** System checks that referrer ID ≠ referred user ID
3. **Duplicate Prevention:** Users who have already been referred cannot submit another code
4. **Code Uniqueness:** Each referral code is guaranteed to be unique
5. **Rate Limiting:** Referral endpoints are protected (future enhancement)

## Frontend Components

### 1. Referral Modal (`dashboard.html`)
- Beautiful welcome modal with gift icon
- Input field for referral code (8 characters, auto-uppercase)
- "Submit" and "Skip" buttons
- Shows bonus amount ($50)
- Only appears once per user

### 2. Referrals Tab (`dashboard.html`)
- Referral link display with copy button
- Three stat boxes:
  - Total Referrals
  - Total Earnings
  - Active Referrals
- Table showing all referred users with details

### 3. JavaScript Functions (`dashboard.js`)
- `checkAndShowReferralModal()` - Shows modal for new users
- `handleReferralSubmission()` - Submits referral code
- `loadReferralData()` - Loads referral statistics
- `displayReferredUsers()` - Displays referred users table
- `copyReferralLink()` - Copies link to clipboard

## Testing the Referral System

### Test Scenario 1: Generate Referral Link

1. Login to dashboard
2. Click "Referrals" tab
3. Verify unique referral link is displayed
4. Click "Copy Link" button
5. Verify link is copied to clipboard

### Test Scenario 2: Refer a New User

1. User A logs in and gets their referral link
2. User B registers a new account
3. User B logs into dashboard
4. User B sees the referral modal
5. User B enters User A's referral code
6. Verify:
   - Success message is shown
   - User A's wallet is credited with $50
   - User B appears in User A's referrals list

### Test Scenario 3: Validation

1. Try to submit an invalid code → Should show error
2. Try to submit the same code twice → Should show "already referred" error
3. Try to use your own referral code → Should show "cannot refer yourself" error

## Future Enhancements

### Potential Features:

1. **Multi-Tier Referrals**
   - Earn bonuses from referrals of your referrals
   - Different bonus amounts for different tiers

2. **Referral Leaderboard**
   - Show top referrers
   - Gamification with badges and achievements

3. **Custom Referral Codes**
   - Allow users to customize their referral code
   - E.g., `JOHN2025` instead of random code

4. **Conditional Bonuses**
   - Bonus only credited when referred user makes first investment
   - Variable bonus amounts based on referred user's activity

5. **Referral Analytics**
   - Conversion rates
   - Click tracking
   - Geographic data

6. **Social Sharing**
   - One-click sharing to Facebook, Twitter, WhatsApp
   - Pre-filled share messages

7. **Email Invitations**
   - Send referral invitations directly from dashboard
   - Track invitation status

8. **Referral Campaigns**
   - Limited-time bonus increases
   - Special events with higher rewards

## Troubleshooting

### Issue: Referral code not appearing

**Solution:** The code is generated on first access. Try reloading the Referrals tab.

### Issue: Referral modal not showing

**Solution:**
- Clear localStorage (`localStorage.removeItem('hasSeenReferralModal')`)
- Refresh the dashboard page

### Issue: "Invalid referral code" error

**Solution:**
- Verify the code is exactly 8 characters
- Check that the referrer exists in the system
- Ensure code is entered in uppercase

### Issue: Bonus not credited to wallet

**Solution:**
- Check MongoDB `referrals` collection for the referral record
- Verify the referrer's wallet balance was updated
- Check server logs for errors

## Support

For issues or questions about the referral system:
- Email: support@tedbrokers.com
- API Documentation: http://localhost:8000/docs

---

**Last Updated:** October 2025
**Version:** 1.0.0
**Author:** TED Brokers Development Team
