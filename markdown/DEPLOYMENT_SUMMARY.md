# 🚀 Deployment Setup Complete!

Your project is now configured for deployment with:
- **Frontend**: Vercel
- **Backend**: Render  
- **Database**: MongoDB Atlas

---

## ✅ Files Created/Updated

### New Files:
1. **`render.yaml`** - Render backend configuration
2. **`vercel.json`** - Vercel frontend configuration
3. **`.env.example`** - Environment variables template
4. **`runtime.txt`** - Python version specification
5. **`DEPLOYMENT_GUIDE.md`** - Complete deployment guide
6. **`QUICK_DEPLOY.md`** - Quick reference checklist
7. **`update_api_urls.js`** - Helper script to update API URLs

### Updated Files:
1. **`config.py`** - Now uses environment variables for MongoDB URI and PORT
2. **`events_api.js`** - API URL configured for production (needs your Render URL)
3. **`list_event.js`** - API URL configured for production (needs your Render URL)
4. **`README.md`** - Added deployment section

---

## 📋 Step-by-Step Deployment Instructions

### STEP 1: Setup MongoDB Atlas (5 minutes)

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create a **FREE (M0) cluster**
4. **Create Database User**:
   - Go to "Database Access" → "Add New Database User"
   - Username: `admin` (or your choice)
   - Password: Create a strong password (SAVE IT!)
   - Privileges: "Atlas admin"
5. **Whitelist IP Addresses**:
   - Go to "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
6. **Get Connection String**:
   - Go to "Database" → Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your password
   - Example: `mongodb+srv://admin:YourPassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

---

### STEP 2: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/your-repo-name.git
git branch -M main
git push -u origin main
```

---

### STEP 3: Deploy Backend to Render (10 minutes)

1. **Go to Render**: https://render.com
2. **Sign up/Login** with GitHub
3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository
4. **Configure Service**:
   ```
   Name: crypto-events-api
   Environment: Python 3
   Region: Choose closest to you
   Branch: main
   Root Directory: (leave empty)
   Build Command: pip install -r requirements.txt
   Start Command: python api_server.py
   ```
5. **Add Environment Variables**:
   - Click "Advanced" → "Add Environment Variable"
   - **Key**: `MONGODB_URI`
   - **Value**: Your MongoDB Atlas connection string (from Step 1)
   - Click "Add"
   - Add another:
     - **Key**: `PYTHON_VERSION`
     - **Value**: `3.11.0`
6. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - **Copy your app URL**: `https://your-app-name.onrender.com`
   - ⚠️ **SAVE THIS URL** - You'll need it for the frontend!

---

### STEP 4: Update Frontend API URLs

**IMPORTANT**: Replace `your-render-app` with your actual Render app name!

**File: `events_api.js`** (Line 2-4)
```javascript
const API_BASE_URL = 'https://your-app-name.onrender.com/api';
```

**File: `list_event.js`** (Line 2-4)
```javascript
const API_BASE = 'https://your-app-name.onrender.com/api';
```

**Or use the helper script:**
```bash
node update_api_urls.js https://your-app-name.onrender.com
```

**Then commit and push:**
```bash
git add events_api.js list_event.js
git commit -m "Update API URLs for production"
git push
```

---

### STEP 5: Deploy Frontend to Vercel (5 minutes)

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** with GitHub
3. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select your repository
4. **Configure**:
   - Framework Preset: **Other** (or leave default)
   - Root Directory: `./` (leave empty)
   - Build Command: (leave empty - static files)
   - Output Directory: (leave empty)
   - Install Command: (leave empty)
5. **Deploy**:
   - Click "Deploy"
   - Wait 1-2 minutes
   - **Copy your frontend URL**: `https://your-project.vercel.app`

---

### STEP 6: Test Your Deployment

1. **Visit your Vercel URL**
2. **Open browser console** (F12) to check for errors
3. **Test features**:
   - View events list
   - Search/filter events
   - Click "List Event" button
   - Submit a test event

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: Backend not starting
- **Solution**: Check Render logs → Go to your service → "Logs"
- Verify `MONGODB_URI` environment variable is set correctly

**Problem**: MongoDB connection failed
- **Solution**: 
  - Check MongoDB Atlas IP whitelist includes `0.0.0.0/0`
  - Verify connection string format
  - Check database user credentials

**Problem**: CORS errors in browser
- **Solution**: The CORS is already configured in `api_server.py` with `CORS(app)`
- If needed, update to allow specific domain:
  ```python
  CORS(app, resources={r"/api/*": {"origins": ["https://your-project.vercel.app"]}})
  ```

### Frontend Issues

**Problem**: API calls failing (404 or CORS)
- **Solution**: 
  - Verify API URL in `events_api.js` and `list_event.js` matches your Render URL
  - Check browser console for exact error
  - Test backend directly: Visit `https://your-app.onrender.com/api/events`

**Problem**: Events not loading
- **Solution**:
  - Check if backend is running (visit Render dashboard)
  - Verify MongoDB has events (check MongoDB Atlas)
  - Check browser console for errors

---

## 📝 Important URLs to Save

After deployment, save these URLs:

- **Backend URL**: `https://your-app-name.onrender.com`
- **Frontend URL**: `https://your-project.vercel.app`
- **MongoDB Atlas Dashboard**: https://cloud.mongodb.com
- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard

---

## 🔄 Updating Your Deployment

### Update Backend:
1. Make changes to Python files
2. Commit and push to GitHub
3. Render will auto-deploy

### Update Frontend:
1. Make changes to HTML/CSS/JS files
2. Commit and push to GitHub
3. Vercel will auto-deploy

### Update API URLs:
If you change your Render backend URL, update:
- `events_api.js` (line 2)
- `list_event.js` (line 2)
- Commit and push

---

## 💰 Cost

**All Free Tier:**
- ✅ Vercel: Free (Hobby plan)
- ✅ Render: Free (750 hours/month)
- ✅ MongoDB Atlas: Free (M0 tier - 512MB)

**Total**: $0/month

**Note**: Render free tier spins down after 15 minutes of inactivity (cold start ~30 seconds)

---

## 🎯 Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Test your live application
4. ⚙️ Set up custom domain (optional)
5. 📊 Monitor usage and logs
6. 🔄 Set up automated scraping (optional)

---

## 📚 Additional Resources

- **Full Guide**: See `DEPLOYMENT_GUIDE.md` for detailed instructions
- **Quick Reference**: See `QUICK_DEPLOY.md` for checklist
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com

---

## ✅ Deployment Checklist

- [ ] MongoDB Atlas account created
- [ ] MongoDB cluster created and configured
- [ ] Database user created
- [ ] IP whitelist configured
- [ ] Connection string saved
- [ ] Code pushed to GitHub
- [ ] Backend deployed to Render
- [ ] Render URL saved
- [ ] Frontend API URLs updated
- [ ] Frontend deployed to Vercel
- [ ] Application tested and working

---

**🎉 You're all set! Happy deploying!**
