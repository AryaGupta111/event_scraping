# 🚀 Quick Deployment Checklist

Follow these steps in order for successful deployment.

---

## ✅ Pre-Deployment (5 minutes)

- [ ] **MongoDB Atlas** connection string ready
- [ ] **GitHub** account created
- [ ] **Render** account created (https://render.com)
- [ ] Code is working locally (`python api_server.py`)

---

## 📦 Step 1: Push to GitHub (2 minutes)

```bash
git init
git add .
git commit -m "Ready for Render deployment"
git remote add origin https://github.com/yourusername/crypto-events.git
git push -u origin main
```

---

## 🌐 Step 2: Deploy on Render (10 minutes)

1. **Go to Render**: https://render.com
2. **Click**: New + → Blueprint
3. **Connect**: Your GitHub repository
4. **Click**: Apply (Render detects `render.yaml`)
5. **Add Environment Variables**:
   - `MONGODB_URI` = Your MongoDB connection string
   - `PORT` = 5000
   - `PYTHON_VERSION` = 3.11.0
6. **Click**: Create Blueprint
7. **Wait**: 5-10 minutes for deployment

---

## 🔗 Step 3: Get Your API URL (1 minute)

1. Go to **crypto-events-api** service
2. Copy the URL: `https://crypto-events-api.onrender.com`
3. Test: Open `https://crypto-events-api.onrender.com/api/health`

---

## 🎨 Step 4: Update Frontend (3 minutes)

### Option A: Use Script (Recommended)

```bash
python update_api_url.py https://crypto-events-api.onrender.com
```

### Option B: Manual Update

Open `events_api.js` and update:

```javascript
const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
    ? 'http://localhost:5000/api' 
    : 'https://crypto-events-api.onrender.com/api';
```

---

## 🌍 Step 5: Deploy Frontend on Vercel (5 minutes)

1. **Go to Vercel**: https://vercel.com
2. **Sign up** with GitHub
3. **Click**: New Project
4. **Import**: Your repository
5. **Click**: Deploy
6. **Done**: Your frontend is live!

---

## 🔧 Step 6: Custom Domain (Optional - 10 minutes)

### On Hostinger:

1. Go to **DNS Settings**
2. Add **CNAME Record**:
   ```
   Name: events
   Points to: crypto-events-api.onrender.com
   TTL: 3600
   ```

### On Render:

1. Go to **crypto-events-api** → Settings
2. Click **Custom Domain**
3. Add: `events.yourdomain.com`
4. Wait for SSL (5-10 minutes)

### Update Frontend:

```javascript
const API_BASE_URL = 'https://events.yourdomain.com/api';
```

---

## ✅ Step 7: Verify Everything (5 minutes)

### Test API:

```bash
curl https://crypto-events-api.onrender.com/api/health
curl https://crypto-events-api.onrender.com/api/events
curl https://crypto-events-api.onrender.com/api/stats
```

### Test Frontend:

1. Open your Vercel URL
2. Events should load
3. Check browser console (F12)

### Test Cron Job:

1. Go to **crypto-events-scraper** on Render
2. Click **Manual Deploy** to test
3. Check logs for success

---

## 🎉 Success Indicators

- ✅ API health endpoint returns `{"success": true}`
- ✅ Events load on frontend
- ✅ No errors in browser console
- ✅ Cron job shows in Render dashboard
- ✅ Custom domain works (if configured)

---

## 🐛 Quick Troubleshooting

### API Not Working?
- Check Render logs
- Verify MongoDB URI in environment variables
- Restart service

### Frontend Not Loading Events?
- Check API URL in `events_api.js`
- Open browser console (F12) for errors
- Test API directly with curl

### Cron Job Not Running?
- Check cron job logs on Render
- Manual trigger to test
- Verify MongoDB connection

---

## 📊 What You Get (Free Tier)

- ✅ Flask API running 24/7
- ✅ Daily scraper at midnight UTC
- ✅ ~720 hours/month usage (within 750 limit)
- ✅ Auto-deploy from GitHub
- ✅ Free SSL certificate
- ✅ Custom domain support

---

## 💰 Costs

- **Render Free Tier**: $0/month
- **Vercel Free Tier**: $0/month
- **MongoDB Atlas Free**: $0/month
- **Hostinger Domain**: (you already have)
- **Total**: $0/month ✅

---

## 🔄 Future Updates

```bash
# Make changes
git add .
git commit -m "Your update message"
git push

# Render auto-deploys in 2-5 minutes
```

---

## 📞 Need Help?

1. Check **RENDER_DEPLOYMENT_GUIDE.md** for detailed instructions
2. View Render logs for errors
3. Test API endpoints with curl
4. Check browser console for frontend issues

---

**Total Time**: ~30-40 minutes for complete deployment

**Difficulty**: Easy (just follow the steps)

**Result**: Professional crypto events platform with automated scraping! 🎉
