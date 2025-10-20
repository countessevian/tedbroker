# Security Features Implementation

This document outlines the advanced security features implemented for TED Brokers.

## 1. Rate Limiting on Login Attempts

### Overview
Protects against brute force attacks and API abuse by limiting the number of requests from a single IP address.

### Implementation
- **Library**: `slowapi` (rate limiting middleware for FastAPI)
- **Storage**: In-memory (can be upgraded to Redis for production)
- **Strategy**: Fixed-window rate limiting

### Rate Limits by Endpoint

| Endpoint | Limit | Description |
|----------|-------|-------------|
| `/api/auth/login` | 5/minute | 5 login attempts per minute per IP |
| `/api/auth/register` | 3/minute | 3 registration attempts per minute |
| `/api/auth/verify-2fa` | 10/minute | 10 2FA verification attempts per minute |
| `/api/auth/resend-2fa` | 3/minute | 3 resend code requests per minute |
| `/api/auth/change-password` | 3/minute | 3 password change attempts per minute |
| `/api/auth/delete-account` | 1/minute | 1 account deletion per minute |
| General API | 100/minute | Default rate limit for other endpoints |
| Global Default | 1000/hour | Overall cap per IP address |

### How It Works
1. Each request is tracked by IP address (considering proxies)
2. If limit exceeded, user receives `429 Too Many Requests` error
3. Rate limits reset after the specified time window
4. Supports X-Forwarded-For and X-Real-IP headers for proxy detection

### Files
- `app/rate_limiter.py` - Rate limiting configuration and middleware
- `main.py` - Rate limiter integration into FastAPI app

---

## 2. IP-Based Security Alerts

### Overview
Automatically detects and alerts users about suspicious login activity based on IP address, location, device, and login patterns.

### Suspicious Activity Detection

The system monitors for:
- **Different Country**: Login from a different country than last successful login
- **Multiple Failed Attempts**: 3+ failed login attempts in last 15 minutes
- **Multiple IPs**: Login attempts from 3+ different IPs in 30 minutes
- **Rapid Login Attempts**: Multiple logins within 1 minute

### Risk Levels
- **Low**: Minor anomaly detected
- **Medium**: Unusual activity that requires attention
- **High**: Strong indicators of account compromise

### Email Alerts

Users receive professional email notifications for:

#### Suspicious Login Alert
- **Trigger**: When suspicious activity is detected during login
- **Contains**: 
  - Risk level (Low/Medium/High)
  - Reasons for flagging
  - Detailed login attempt information (time, IP, location, device, browser, OS)
  - Action buttons (Change Password, View Security Settings)
  - Security recommendations

#### Successful Login Notification
- **Trigger**: Successful login from new location/device (optional feature)
- **Contains**:
  - Login time and location details
  - Device and browser information
  - Quick access to security settings

### Files
- `app/security_alerts.py` - Security alert service and email templates
- `app/email_service.py` - Email delivery via SendGrid

---

## 3. Login History Tracking

### Overview
Comprehensive tracking system that records every login attempt with detailed metadata for security analysis and user transparency.

### Data Collected

For each login attempt, the system tracks:
- **User Information**: Email, User ID
- **Status**: Success or failure (with failure reason)
- **Timestamp**: Exact date and time
- **IP Address**: Real IP (considering proxies)
- **Device Information**:
  - Device type (mobile, tablet, desktop)
  - Operating system and version
  - Browser and version
  - Full user agent string
- **Location**: Approximate location based on IP (country, region, city)

### Features

#### Login History API
- **Endpoint**: `GET /api/auth/login-history`
- **Authentication**: Required (JWT token)
- **Parameters**:
  - `limit`: Number of records to return (default: 50)
  - `offset`: Pagination offset (default: 0)
- **Returns**: Array of login attempts with full metadata

#### Login Statistics API
- **Endpoint**: `GET /api/auth/login-statistics`
- **Authentication**: Required (JWT token)
- **Parameters**:
  - `days`: Analysis period in days (default: 30)
- **Returns**:
  ```json
  {
    "total_attempts": 45,
    "successful_logins": 40,
    "failed_logins": 5,
    "unique_ips": 3,
    "unique_devices": 2,
    "most_recent_login": "2025-10-20T12:30:00Z",
    "most_recent_ip": "192.168.1.1"
  }
  ```

#### Suspicious Activity Analysis
- Automatic analysis of login patterns
- Detects anomalies in location, timing, and behavior
- Provides risk assessment for each login attempt

### Database Collection
- **Collection Name**: `login_history`
- **Fields**: email, user_id, ip_address, success, failure_reason, timestamp, device_info, location

### Files
- `app/login_history.py` - Login history tracking and analytics service

---

## How Security Features Work Together

### Normal Login Flow
1. User enters email and password
2. **Rate Limiter** checks if within limits (5 attempts/minute)
3. System validates credentials
4. **Login History** records the attempt
5. **Suspicious Activity** detector analyzes login patterns
6. If suspicious, **Security Alert** email is sent
7. 2FA code is generated and emailed
8. User enters 2FA code (rate limited to 10/minute)
9. **Login History** records successful login
10. User gets access token

### When Suspicious Activity Detected
1. User attempts login
2. System detects unusual patterns (e.g., different country)
3. **Security Alert** email sent immediately
4. Login proceeds normally with 2FA
5. User can review login history in dashboard
6. User can take action if unauthorized

### Protection Against Brute Force
1. Attacker attempts multiple logins
2. **Rate Limiter** blocks after 5 attempts/minute
3. **Login History** records all failed attempts
4. **Suspicious Activity** detector flags the behavior
5. **Security Alert** notifies the legitimate user
6. Attacker is forced to wait before retry
7. Admin can review failed attempts and block IP

---

## API Endpoints

### Authentication Endpoints (Rate Limited)
- `POST /api/auth/register` - 3/minute
- `POST /api/auth/login` - 5/minute
- `POST /api/auth/verify-2fa` - 10/minute
- `POST /api/auth/resend-2fa` - 3/minute

### Security Monitoring Endpoints
- `GET /api/auth/login-history` - View login history
- `GET /api/auth/login-statistics` - View login statistics

### Error Responses
- **429 Too Many Requests**: Rate limit exceeded
- **401 Unauthorized**: Invalid credentials
- **403 Forbidden**: Account inactive or blocked

---

## Configuration

### Environment Variables

```env
# SendGrid for security alerts
SENDGRID_API_KEY=your-api-key
SENDGRID_FROM_EMAIL=noreply@tedbrokers.com
SENDGRID_FROM_NAME=TED Brokers

# Rate Limiting (optional - defaults shown)
RATE_LIMIT_STORAGE=memory://  # Use redis://localhost:6379 for production
RATE_LIMIT_STRATEGY=fixed-window
```

### Upgrading to Redis (Production)

For distributed systems and persistence, upgrade to Redis:

1. Install Redis:
   ```bash
   pip install redis
   ```

2. Update `app/rate_limiter.py`:
   ```python
   limiter = Limiter(
       key_func=get_real_ip,
       storage_uri="redis://localhost:6379",
       strategy="fixed-window"
   )
   ```

---

## Security Best Practices

### For Administrators
1. **Monitor Login History**: Regularly review failed login attempts
2. **Analyze Patterns**: Look for suspicious patterns in login statistics
3. **Update Rate Limits**: Adjust based on legitimate user behavior
4. **Enable Alerts**: Ensure SendGrid is configured for security alerts
5. **Use Redis**: In production, use Redis for distributed rate limiting

### For Users
1. **Review Login History**: Check dashboard regularly for unauthorized access
2. **Respond to Alerts**: Act immediately on suspicious login emails
3. **Use Strong Passwords**: Combine with 2FA for maximum security
4. **Report Issues**: Contact support if unauthorized access detected

### For Developers
1. **Proxy Headers**: Ensure reverse proxy passes X-Forwarded-For header
2. **IP Geolocation**: Consider integrating ipapi.co or ipstack for accurate location data
3. **Log Monitoring**: Set up alerts for high failure rates
4. **Backup**: Regular backups of login_history collection
5. **Cleanup**: Implement periodic cleanup of old login records

---

## Testing the Security Features

### Test Rate Limiting
```bash
# Make 6 rapid login attempts (should block on 6th)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"Test123"}' \
    -w "\nStatus: %{http_code}\n\n"
  sleep 1
done
```

### Test Login History
```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login ... | jq -r '.access_token')

# View login history
curl http://localhost:8000/api/auth/login-history \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Test Security Alerts
1. Login from normal location
2. Use VPN to login from different country
3. Check email for security alert

---

## Troubleshooting

### Rate Limit Not Working
- Check `app.state.limiter` is set in main.py
- Verify rate limiter decorator on routes
- Test with different IP addresses

### Security Alerts Not Sending
- Verify SendGrid API key is configured
- Check email service logs for errors
- Ensure SendGrid sender is verified

### Login History Empty
- Verify MongoDB connection
- Check `login_history` collection exists
- Ensure login attempts are being recorded

---

## Future Enhancements

### Planned Features
1. **IP Blocking**: Automatic IP blocking after repeated failures
2. **Device Fingerprinting**: More sophisticated device tracking
3. **Geolocation Integration**: Real-time IP geolocation service
4. **Admin Dashboard**: Visual analytics for security monitoring
5. **Export History**: CSV/PDF export of login history
6. **Anomaly Detection**: Machine learning for advanced threat detection
7. **Session Management**: Force logout from specific devices
8. **Security Score**: User security score based on behavior

### Integration Points
- **Slack/Discord**: Notify admins of security events
- **Datadog/Grafana**: Metrics and monitoring
- **MaxMind**: Professional IP geolocation
- **Cloudflare**: Enterprise DDoS protection

---

## Support

For security concerns or questions:
- Email: security@tedbrokers.com
- Documentation: /docs/security
- API Docs: http://localhost:8000/docs

**Last Updated**: October 2025
**Version**: 1.0.0
