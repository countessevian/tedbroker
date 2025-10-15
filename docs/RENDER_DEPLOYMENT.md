# Deploying TED Broker to Render

This guide explains how to deploy the TED Broker FastAPI application to Render.

## Prerequisites

1. A [Render account](https://render.com)
2. GitHub repository with the code (already set up at `countessevian/tedbroker`)
3. A MongoDB database (MongoDB Atlas or Render-hosted)

## Deployment Steps

### 1. Create a New Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `countessevian/tedbroker`
4. Choose the repository and click **"Connect"**

### 2. Configure the Web Service

Fill in the following settings:

#### Basic Settings
- **Name**: `tedbroker` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `master` (or `main` if you renamed it)
- **Root Directory**: Leave empty (root of repository)
- **Runtime**: `Python 3`

#### Build & Deploy Settings

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Instance Settings
- **Instance Type**:
  - Free tier (for testing) - sleeps after inactivity
  - Starter ($7/month) - recommended for production
  - Or higher tiers based on your needs

### 3. Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

| Key | Value | Notes |
|-----|-------|-------|
| `MONGODB_URL` | Your MongoDB connection string | e.g., `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DATABASE_NAME` | `tedbroker` | Your database name |
| `SECRET_KEY` | Generate new key (see below) | **CRITICAL: Never use the one from .env** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |
| `PYTHON_VERSION` | `3.11` | Optional: specify Python version |

**Generate a secure SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Run the build command
   - Start your application
3. Monitor the deploy logs for any errors

### 5. Set Up MongoDB Database

#### Option A: MongoDB Atlas (Recommended)
1. Create free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create database user
3. Whitelist Render IPs (or use `0.0.0.0/0` for simplicity)
4. Get connection string and add to `MONGODB_URL` environment variable

#### Option B: Render MongoDB (Paid)
1. In Render Dashboard, create a new MongoDB instance
2. Link it to your web service
3. Use the provided connection string

### 6. Custom Domain (Optional)

1. In your web service settings, go to **"Settings"** → **"Custom Domain"**
2. Add your domain (e.g., `tedbroker.com`)
3. Configure DNS records as instructed by Render
4. Render provides free SSL certificates

## Post-Deployment

### Verify Deployment
- Check your service URL: `https://tedbroker.onrender.com`
- Test API endpoints: `https://tedbroker.onrender.com/docs`
- Test frontend: `https://tedbroker.onrender.com/`

### Update CORS Settings
In `main.py`, update CORS origins for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tedbroker.onrender.com",
        "https://yourdomain.com"  # Add your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Monitor Your Application
- View logs in Render Dashboard → Your Service → **"Logs"**
- Set up metrics and alerts in **"Metrics"** tab
- Monitor database usage

## Troubleshooting

### Build Fails
- Check build logs in Render Dashboard
- Verify `requirements.txt` is valid
- Ensure Python version compatibility

### Application Won't Start
- Check start command is correct
- Verify environment variables are set
- Check logs for Python errors

### Database Connection Issues
- Verify `MONGODB_URL` is correct
- Check MongoDB Atlas IP whitelist
- Ensure database user has proper permissions

### Static Files Not Loading
- Verify `public/` directory is in repository
- Check static file mounts in `main.py`
- Ensure paths are correct in HTML files

## Continuous Deployment

Render automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update feature"
git push gh_countessevian master
```

Render will:
1. Detect the push
2. Run build command
3. Deploy new version
4. Zero-downtime deployment (on paid plans)

## Scaling

As your application grows:
1. Upgrade instance type in Render Dashboard
2. Enable autoscaling (available on higher tiers)
3. Consider horizontal scaling with multiple instances
4. Add Redis for caching/sessions
5. Use CDN for static assets

## Security Checklist

- ✅ `.env` file is in `.gitignore`
- ✅ New `SECRET_KEY` generated for production
- ✅ MongoDB credentials are secure
- ✅ CORS origins are restricted to your domains
- ✅ HTTPS is enabled (automatic with Render)
- ✅ Environment variables set in Render (not in code)

## Costs

### Free Tier
- 750 hours/month free
- Spins down after 15 minutes of inactivity
- Spins up on request (may take 30+ seconds)

### Starter ($7/month)
- Always on
- 512MB RAM
- Good for small production apps

### Standard ($25+/month)
- More resources
- Better performance
- Production-ready

## Support

- [Render Documentation](https://render.com/docs)
- [FastAPI on Render](https://render.com/docs/deploy-fastapi)
- [Render Community](https://community.render.com/)
