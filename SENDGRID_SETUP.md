# SendGrid Setup Guide for TED Brokers 2FA

This guide will help you set up SendGrid to enable email-based 2FA for production.

## Step 1: Create a SendGrid Account

1. Go to [SendGrid Sign Up](https://signup.sendgrid.com/)
2. Fill in your details and create an account
3. Complete email verification
4. Choose the **Free Plan** (100 emails/day) or a paid plan based on your needs

## Step 2: Verify Your Sender Identity

SendGrid requires you to verify your sender email or domain before sending emails.

### Option A: Single Sender Verification (Quickest)

1. Go to [Sender Authentication](https://app.sendgrid.com/settings/sender_auth)
2. Click **"Verify a Single Sender"**
3. Fill in the form:
   - **From Name**: TED Brokers
   - **From Email Address**: noreply@tedbrokers.com (or your actual email)
   - **Reply To**: support@tedbrokers.com (or your support email)
   - **Company Address**: Your business address
4. Click **"Create"**
5. Check your email and click the verification link
6. Once verified, you can use this email as `SENDGRID_FROM_EMAIL`

### Option B: Domain Authentication (Recommended for Production)

1. Go to [Sender Authentication](https://app.sendgrid.com/settings/sender_auth)
2. Click **"Authenticate Your Domain"**
3. Select your DNS provider
4. Enter your domain: `tedbrokers.com`
5. Follow the instructions to add DNS records to your domain
6. Wait for DNS propagation (can take up to 48 hours)
7. Once verified, you can send from any email @tedbrokers.com

## Step 3: Create an API Key

1. Go to [API Keys](https://app.sendgrid.com/settings/api_keys)
2. Click **"Create API Key"**
3. Enter a name: `TED_Brokers_2FA_Production`
4. Select **"Full Access"** (or "Restricted Access" with Mail Send permissions)
5. Click **"Create & View"**
6. **IMPORTANT**: Copy the API key immediately - you won't be able to see it again!
7. The API key will look like: `SG.xxxxxxxxxxxxxxxxxxxxxxxx`

## Step 4: Update Your .env File

Open `/home/taliban/websites/tedbroker.com/.env` and update:

```env
# Replace with your actual SendGrid API key
SENDGRID_API_KEY=SG.your-actual-api-key-here

# Update with your verified sender email
SENDGRID_FROM_EMAIL=noreply@tedbrokers.com

# Optional: Change the from name
SENDGRID_FROM_NAME=TED Brokers
```

**Security Note**: Never commit your `.env` file to version control! The API key should be kept secret.

## Step 5: Test the Configuration

1. Restart your application:
   ```bash
   # Kill existing process
   ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}' | xargs kill -9
   
   # Start the server
   python3 main.py
   ```

2. Try registering a new user or logging in
3. Check your email for the verification code
4. If emails aren't arriving:
   - Check your spam folder
   - Verify the sender email in SendGrid
   - Check SendGrid Activity Feed: https://app.sendgrid.com/email_activity

## Step 6: Monitor Email Activity

- View email stats: [SendGrid Statistics](https://app.sendgrid.com/statistics)
- Track individual emails: [Email Activity](https://app.sendgrid.com/email_activity)
- Check bounces and blocks: [Suppressions](https://app.sendgrid.com/suppressions)

## Free Plan Limits

The SendGrid Free Plan includes:
- **100 emails per day**
- Email validation
- Bounce/spam reports
- Basic analytics

If you need more emails, upgrade to a paid plan.

## Troubleshooting

### Emails not sending?

1. **Check API Key**: Make sure it's copied correctly without extra spaces
2. **Verify Sender**: Ensure your sender email is verified in SendGrid
3. **Check Logs**: Look at your application logs for error messages
4. **SendGrid Activity**: Check the Email Activity feed in SendGrid dashboard

### Common Error Messages:

- **"The from email does not match a verified Sender Identity"**
  - Solution: Complete Single Sender or Domain Authentication

- **"API key is invalid"**
  - Solution: Create a new API key and update .env file

- **"Rate limit exceeded"**
  - Solution: Upgrade your SendGrid plan or wait for rate limit reset

## Production Recommendations

1. **Use Domain Authentication** instead of Single Sender for better deliverability
2. **Set up DKIM and SPF** records through Domain Authentication
3. **Monitor your sender reputation** in SendGrid dashboard
4. **Implement email throttling** if sending high volumes
5. **Add unsubscribe links** for marketing emails (not required for 2FA)
6. **Keep your API keys secure** and rotate them periodically

## Support

- SendGrid Documentation: https://docs.sendgrid.com/
- SendGrid Support: https://support.sendgrid.com/
- TED Brokers Support: support@tedbrokers.com

---

**Note**: After configuration, restart your application for changes to take effect!
