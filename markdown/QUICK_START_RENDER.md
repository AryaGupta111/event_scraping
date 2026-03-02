# ⚡ Quick Start - Deploy to Render in 15 Minutes

The fastest way to get your app live on Render with automated scraping.

---

## 🎯 What You'll Get

- ✅ Live API at `https://your-app.onrender.com`
- ✅ Automated daily scraping at midnight UTC
- ✅ Free tier (stays within 750 hours/month)
- ✅ Auto-deploy from GitHub
- ✅ Free SSL certificate

---

## 📋 Before You Start

Make sure you have:
1. ✅ MongoDB Atlas connection string
2. ✅ GitHub account
3. ✅ 15 minutes of time

---

## 🚀 Step-by-Step (15 minutes)

### 1️⃣ Push to GitHub (3 min)

```bash
# If not already initialized
git init
git add .
git commit -m "Ready for Render deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

### 2️⃣ Deploy on Render (5 min)

1. **Go to**: https://render.com
2. **Sign up** with GitHub
3. **Click**: "New +" → "Blueprint"
4. **Select**: Your repository
5. **Click**: "Apply"

Render will detect `render.yaml` and create:
- ✅ Web Service (Flask API)
- ✅ Cron Job (Daily scraper)

---

### 3️⃣ Add Environment Variables (2 min)

For **crypto-events-api** service:

```
MONGODB_URI = mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0
PORT = 5000
PYTHON_VERSION = 3.11.0
```

For **crypto-events-scraper** cron job:

```
MONGODB_URI = mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0
PYTHON_VERSION = 3.11.0
```

⚠️ **Replace with YOUR MongoDB URI!**

---

### 4️⃣ Wait for Deployment (5 min)

Watch the logs as Render:
- Installs dependencies
- Starts your API
- Schedules the cron job

---

### 5️⃣ Test Your API (1 min)

Once deployed, test these URLs:

```bash
# Health check
https://crypto-events-api.onrender.com/api/health

# Get events
https://crypto-events-api.onrender.com/api/events

# Get stats
https://crypto-events-api.onrender.com/api/stats
```

---

### 6️⃣ Update Frontend (2 min)

**Option A: Use Script**
```bash
python update_api_url.py https://crypto-events-api.onrender.com
```

**Option B: Manual**

Open `events_api.js` and update line 3:

```javascript
const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
    ? 'http://localhost:5000/api' 
    : 'https://crypto-events-api.onrender.com/api';
```

---

### 7️⃣ Deploy Frontend on Vercel (5 min)

1. **Go to**: https://vercel.com
2. **Sign up** with GitHub
3. **Click**: "New Project"
4. **Import**: Your repository
5. **Deploy**: Click deploy

Done! Your frontend is live.

---

## ✅ Verification Checklist

- [ ] API health endpoint works
- [ ] Events endpoint returns data
- [ ] Frontend loads events
- [ ] No errors in browser console
- [ ] Cron job appears in Render dashboard

---

## 🎉 You're Live!

Your app is now deployed with:
- ✅ API: `https://crypto-events-api.onrender.com`
- ✅ Frontend: `https://your-app.vercel.app`
- ✅ Daily scraping: Midnight UTC
- ✅ Cost: $0 (free tier)

---

## 🔧 Optional: Custom Domain

### On Hostinger DNS:

```
Type: CNAME
Name: events
Points to: crypto-events-api.onrender.com
TTL: 3600
```

### On Render:

1. Settings → Custom Domain
2. Add: `events.yourdomain.com`
3. Wait for SSL (5-10 min)

---

## 📊 Monitor Your App

### View Logs:
- Render Dashboard → Service → Logs

### Check Cron Job:
- Render Dashboard → crypto-events-scraper → Logs

### Test Scraper Manually:
- crypto-events-scraper → Manual Deploy

---

## 🔄 Update Your App

```bash
# Make changes
git add .
git commit -m "Update message"
git push

# Render auto-deploys in 2-5 minutes
```

---

## 💡 Pro Tips

1. **First request slow?** Free tier spins down after 15 min. First request takes 30-60 sec.
2. **Need always-on?** Upgrade to Starter ($7/month)
3. **Check logs often** to catch issues early
4. **Test cron job** with manual trigger first

---

## 🐛 Common Issues

### "Build failed"
- Check requirements.txt
- Verify Python version
- Check Render logs

### "Can't connect to MongoDB"
- Verify MONGODB_URI
- Check MongoDB Atlas network access (allow 0.0.0.0/0)
- Test connection locally first

### "Frontend not loading events"
- Check API URL in events_api.js
- Open browser console (F12)
- Test API directly

---

## 📞 Need Help?

- **Detailed Guide**: See `RENDER_DEPLOYMENT_GUIDE.md`
- **Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com

---

## 🎯 Next Steps

1. ✅ Test all features
2. ✅ Add custom domain (optional)
3. ✅ Monitor logs for first 24 hours
4. ✅ Verify cron job runs at midnight
5. ✅ Share your app with the world! 🌍

---

**Total Time**: 15 minutes

**Cost**: $0 (free tier)

**Result**: Professional crypto events platform! 🚀
