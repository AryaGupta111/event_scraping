# Quick Deployment Checklist

## Before You Start
- [ ] MongoDB Atlas account created
- [ ] GitHub repository ready
- [ ] Vercel account created
- [ ] Render account created

---

## Step-by-Step Deployment

### 1. MongoDB Atlas Setup (5 minutes)
```
1. Create free cluster
2. Create database user (save credentials!)
3. Whitelist IP: 0.0.0.0/0
4. Get connection string
```

### 2. Deploy Backend to Render (10 minutes)
```
1. Login to Render → New Web Service
2. Connect GitHub repo
3. Settings:
   - Name: crypto-events-api
   - Build: pip install -r requirements.txt
   - Start: python api_server.py
4. Add env var: MONGODB_URI = (your Atlas connection string)
5. Deploy → Wait for URL: https://xxx.onrender.com
```

### 3. Update Frontend API URLs
```
Edit events_api.js line 2:
const API_BASE_URL = 'https://your-render-app.onrender.com/api';

Edit list_event.js line 2:
const API_BASE = 'https://your-render-app.onrender.com/api';
```

### 4. Deploy Frontend to Vercel (5 minutes)
```
1. Login to Vercel → Add Project
2. Import GitHub repo
3. Deploy (no build needed - static files)
4. Get URL: https://xxx.vercel.app
```

### 5. Test
```
1. Visit Vercel URL
2. Check browser console for errors
3. Test "List Event" functionality
```

---

## Important URLs to Save

- **Backend URL**: `https://your-app.onrender.com`
- **Frontend URL**: `https://your-project.vercel.app`
- **MongoDB Atlas**: https://cloud.mongodb.com

---

## Troubleshooting

**CORS Error?**
- Update CORS in api_server.py to allow your Vercel domain

**API Not Working?**
- Check Render logs
- Verify MONGODB_URI env var is set
- Test backend URL directly: https://your-app.onrender.com/api/events

**Frontend Not Loading?**
- Check browser console
- Verify API URLs are updated correctly
- Check Vercel deployment logs

---

## Files Created for Deployment

- ✅ `render.yaml` - Render configuration
- ✅ `vercel.json` - Vercel configuration  
- ✅ `.env.example` - Environment variables template
- ✅ `runtime.txt` - Python version for Render
- ✅ `DEPLOYMENT_GUIDE.md` - Full detailed guide

---

**Need Help?** Check `DEPLOYMENT_GUIDE.md` for detailed instructions.
