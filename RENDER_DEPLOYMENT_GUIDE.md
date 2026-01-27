# 🚀 Render Deployment Guide (Free Tier with Cron Jobs)

Complete guide to deploy your Crypto Events app on Render with automated daily scraping.

---

## 📋 What You'll Deploy

- ✅ **Web Service**: Flask API (runs 24/7)
- ✅ **Cron Job**: Daily scraper (runs at midnight UTC)
- ✅ **Free Tier**: Stays within 750 hours/month limit
- ✅ **Custom Domain**: Support for Hostinger subdomain

---

## 🎯 Prerequisites

1. ✅ GitHub account
2. ✅ Render account (sign up at https://render.com)
3. ✅ MongoDB Atlas connection string
4. ✅ Your code pushed to GitHub repository

---

## 📦 Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Render deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/crypto-events.git

# Push to GitHub
git push -u origin main
```

### 1.2 Verify Files

Make sure these files are in your repository:
- ✅ `render.yaml` (updated with cron job)
- ✅ `requirements.txt`
- ✅ `api_server.py`
- ✅ `scraper_mongodb.py`
- ✅ `database.py`
- ✅ `config.py`

---

## 🌐 Step 2: Deploy on Render

### 2.1 Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 2.2 Create New Blueprint

1. Click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render will detect `render.yaml` automatically
4. Click **"Apply"**

### 2.3 Configure Environment Variables

For **crypto-events-api** (Web Service):

```
MONGODB_URI = mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0
PORT = 5000
PYTHON_VERSION = 3.11.0
```

For **crypto-events-scraper** (Cron Job):

```
MONGODB_URI = mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0
PYTHON_VERSION = 3.11.0
```

⚠️ **IMPORTANT**: Replace the MongoDB URI with your actual connection string!

### 2.4 Deploy

1. Click **"Create Blueprint"**
2. Wait for deployment (5-10 minutes)
3. Both services will be created:
   - Web Service: `crypto-events-api`
   - Cron Job: `crypto-events-scraper`

---

## 🔗 Step 3: Get Your API URL

After deployment:

1. Go to your **crypto-events-api** service
2. Copy the URL (e.g., `https://crypto-events-api.onrender.com`)
3. Test it: `https://crypto-events-api.onrender.com/api/health`

---

## 🎨 Step 4: Update Frontend API URL

### 4.1 Update events_api.js

Open `events_api.js` and update the API URL:

```javascript
// Replace this line:
const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
    ? 'http://localhost:5000/api' 
    : 'https://your-render-app.onrender.com/api';

// With your actual Render URL:
const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
    ? 'http://localhost:5000/api' 
    : 'https://crypto-events-api.onrender.com/api';
```

### 4.2 Update list_event.js (if exists)

Do the same for any other JavaScript files that call the API.

---

## 🌍 Step 5: Deploy Frontend (Optional)

### Option A: Deploy Frontend on Vercel

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click **"New Project"**
4. Import your repository
5. Vercel will auto-detect settings
6. Click **"Deploy"**

### Option B: Serve Frontend from Render

Add to `render.yaml`:

```yaml
  - type: web
    name: crypto-events-frontend
    env: static
    buildCommand: echo "No build needed"
    staticPublishPath: .
    routes:
      - type: rewrite
        source: /*
        destination: /events_api.html
```

---

## 🔧 Step 6: Configure Custom Domain (Hostinger)

### 6.1 On Hostinger DNS Settings

1. Login to Hostinger
2. Go to **Domains** → **DNS/Nameservers**
3. Add CNAME record:

```
Type: CNAME
Name: events (or api, or whatever you want)
Points to: crypto-events-api.onrender.com
TTL: 3600
```

### 6.2 On Render

1. Go to your **crypto-events-api** service
2. Click **"Settings"** → **"Custom Domain"**
3. Add: `events.yourdomain.com`
4. Wait for SSL certificate (automatic, 5-10 minutes)

### 6.3 Update Frontend API URL

```javascript
const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
    ? 'http://localhost:5000/api' 
    : 'https://events.yourdomain.com/api';
```

---

## ⏰ Step 7: Verify Cron Job

### Check Cron Job Status

1. Go to Render dashboard
2. Click on **crypto-events-scraper**
3. View **"Logs"** to see execution history
4. Cron runs daily at **00:00 UTC** (midnight)

### Manual Trigger (for testing)

1. Go to **crypto-events-scraper** service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. This will run the scraper immediately

### Change Schedule (optional)

Edit `render.yaml`:

```yaml
schedule: "0 0 * * *"   # Midnight UTC daily
schedule: "0 */12 * * *" # Every 12 hours
schedule: "0 8 * * *"    # 8 AM UTC daily
```

---

## 🧪 Step 8: Test Your Deployment

### Test API Endpoints

```bash
# Health check
curl https://crypto-events-api.onrender.com/api/health

# Get events
curl https://crypto-events-api.onrender.com/api/events

# Get stats
curl https://crypto-events-api.onrender.com/api/stats
```

### Test Frontend

1. Open your frontend URL
2. Events should load from Render API
3. Check browser console for errors

---

## 📊 Monitoring & Logs

### View Logs

1. Go to Render dashboard
2. Click on service name
3. Click **"Logs"** tab
4. Real-time logs appear here

### Check Metrics

1. Go to **"Metrics"** tab
2. View:
   - Request count
   - Response time
   - Memory usage
   - CPU usage

---

## 🐛 Troubleshooting

### API Not Responding

1. Check logs for errors
2. Verify MongoDB connection string
3. Check environment variables
4. Restart service

### Cron Job Not Running

1. Check cron job logs
2. Verify schedule syntax
3. Check MongoDB connection
4. Manual trigger to test

### Frontend Can't Connect to API

1. Check API URL in JavaScript
2. Verify CORS settings
3. Check browser console
4. Test API directly with curl

### Free Tier Limitations

- Web service spins down after 15 min inactivity
- First request after spin-down takes 30-60 seconds
- Upgrade to paid ($7/month) for always-on

---

## 💰 Cost Breakdown

### Free Tier (Current Setup)

- **Web Service**: ~720 hours/month
- **Cron Job**: ~1 hour/month (runs daily for ~2 min)
- **Total**: ~721 hours/month ✅ (within 750 limit)
- **Cost**: $0

### Paid Tier (If Needed)

- **Starter Plan**: $7/month
- **Benefits**:
  - Always-on (no spin-down)
  - Faster response times
  - More resources

---

## 🔄 Updating Your App

### Push Updates

```bash
# Make changes to your code
git add .
git commit -m "Update description"
git push

# Render auto-deploys from GitHub
# Wait 2-5 minutes for deployment
```

### Manual Deploy

1. Go to Render dashboard
2. Click service name
3. Click **"Manual Deploy"**
4. Select branch and deploy

---

## 📝 Environment Variables Reference

### Required Variables

```
MONGODB_URI = Your MongoDB Atlas connection string
PORT = 5000 (for web service)
PYTHON_VERSION = 3.11.0
```

### Optional Variables

```
API_HOST = 0.0.0.0
SCRAPE_INTERVAL_HOURS = 24
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Blueprint deployed from render.yaml
- [ ] Environment variables configured
- [ ] Web service running
- [ ] Cron job scheduled
- [ ] API URL updated in frontend
- [ ] Frontend deployed (Vercel or Render)
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] API endpoints tested
- [ ] Cron job tested (manual trigger)
- [ ] Frontend loads events successfully

---

## 🎉 Success!

Your app is now deployed on Render with:
- ✅ Flask API running 24/7
- ✅ Daily automated scraping
- ✅ Free tier (within limits)
- ✅ Custom domain support
- ✅ Auto-deploy from GitHub

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **MongoDB Atlas**: https://www.mongodb.com/docs/atlas

---

**Need help?** Check the logs first, then refer to the troubleshooting section above.
