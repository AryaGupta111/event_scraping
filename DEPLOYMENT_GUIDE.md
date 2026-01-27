# Deployment Guide: Frontend (Vercel) + Backend (Render)

This guide will walk you through deploying your Crypto Events project with:
- **Frontend**: Vercel (Static files)
- **Backend**: Render (Flask API)
- **Database**: MongoDB Atlas (Free tier)

---

## Prerequisites

1. GitHub account
2. Vercel account (free) - Sign up at https://vercel.com
3. Render account (free) - Sign up at https://render.com
4. MongoDB Atlas account (free) - Sign up at https://www.mongodb.com/cloud/atlas

---

## Step 1: Setup MongoDB Atlas

1. **Create MongoDB Atlas Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for free account
   - Choose the **FREE (M0) tier**

2. **Create a Cluster**
   - Click "Build a Database"
   - Select "FREE" tier
   - Choose a cloud provider and region (closest to you)
   - Click "Create"

3. **Create Database User**
   - Go to "Database Access" → "Add New Database User"
   - Choose "Password" authentication
   - Create username and password (save these!)
   - Set privileges to "Atlas admin" or "Read and write to any database"
   - Click "Add User"

4. **Whitelist IP Addresses**
   - Go to "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0) for production
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" → Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Replace `<dbname>` with `crypto_events_db` (or leave as is)
   - Example: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

---

## Step 2: Prepare Your Repository

1. **Update API URLs in Frontend Files**

   Before deploying, update the API URLs in your frontend files:

   **File: `events_api.js`** (Line 2-4)
   ```javascript
   const API_BASE_URL = 'https://your-render-app.onrender.com/api';
   ```

   **File: `list_event.js`** (Line 2-4)
   ```javascript
   const API_BASE = 'https://your-render-app.onrender.com/api';
   ```

   ⚠️ **Important**: Replace `your-render-app` with your actual Render app name (you'll get this after deploying to Render).

2. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ready for deployment"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

---

## Step 3: Deploy Backend to Render

1. **Login to Render**
   - Go to https://render.com
   - Sign up/login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Service**
   - **Name**: `crypto-events-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `./` if needed)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`

4. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable":
   - **Key**: `MONGODB_URI`
   - **Value**: Your MongoDB Atlas connection string (from Step 1)
   
   Click "Add Environment Variable" again:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.11.0`

5. **Deploy**
   - Click "Create Web Service"
   - Render will start building and deploying
   - Wait for deployment to complete (5-10 minutes)
   - Note your app URL: `https://your-app-name.onrender.com`

6. **Test Backend**
   - Visit: `https://your-app-name.onrender.com/api/events`
   - You should see JSON response with events (or empty array if no events)

---

## Step 4: Update Frontend with Backend URL

1. **Update API URLs**
   
   **File: `events_api.js`** (Line 2-4)
   ```javascript
   const API_BASE_URL = 'https://your-app-name.onrender.com/api';
   ```

   **File: `list_event.js`** (Line 2-4)
   ```javascript
   const API_BASE = 'https://your-app-name.onrender.com/api';
   ```

2. **Commit and Push**
   ```bash
   git add events_api.js list_event.js
   git commit -m "Update API URLs for production"
   git push
   ```

---

## Step 5: Deploy Frontend to Vercel

1. **Login to Vercel**
   - Go to https://vercel.com
   - Sign up/login with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select your repository

3. **Configure Project**
   - **Framework Preset**: Other (or leave as default)
   - **Root Directory**: `./` (leave empty)
   - **Build Command**: Leave empty (static files)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

4. **Deploy**
   - Click "Deploy"
   - Vercel will deploy your static files
   - Wait for deployment (1-2 minutes)
   - You'll get a URL like: `https://your-project.vercel.app`

5. **Test Frontend**
   - Visit your Vercel URL
   - The frontend should load and connect to your Render backend
   - Test the "List Event" functionality

---

## Step 6: Configure CORS (If Needed)

If you encounter CORS errors, update `api_server.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
# Allow all origins for production (or specify your Vercel domain)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

Or for specific domain:
```python
CORS(app, resources={r"/api/*": {"origins": ["https://your-project.vercel.app"]}})
```

---

## Step 7: Custom Domain (Optional)

### Vercel Custom Domain
1. Go to your project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### Render Custom Domain
1. Go to your service → Settings → Custom Domains
2. Add your custom domain
3. Configure DNS records

---

## Troubleshooting

### Backend Issues

**Problem**: Backend not starting
- Check Render logs: Go to your service → "Logs"
- Verify `MONGODB_URI` environment variable is set correctly
- Check `requirements.txt` has all dependencies

**Problem**: MongoDB connection failed
- Verify MongoDB Atlas IP whitelist includes Render IPs
- Check connection string format
- Verify database user credentials

**Problem**: CORS errors
- Update CORS settings in `api_server.py`
- Add your Vercel domain to allowed origins

### Frontend Issues

**Problem**: API calls failing
- Check browser console for errors
- Verify API URL in `events_api.js` and `list_event.js`
- Check if backend is running (visit backend URL directly)

**Problem**: 404 errors
- Verify file paths are correct
- Check Vercel deployment logs

---

## Environment Variables Summary

### Render (Backend)
- `MONGODB_URI`: Your MongoDB Atlas connection string
- `PYTHON_VERSION`: 3.11.0

### Vercel (Frontend)
- No environment variables needed (API URL is hardcoded in JS files)

---

## Updating Your Deployment

### Update Backend
1. Make changes to Python files
2. Commit and push to GitHub
3. Render will auto-deploy

### Update Frontend
1. Make changes to HTML/CSS/JS files
2. Update API URLs if backend URL changed
3. Commit and push to GitHub
4. Vercel will auto-deploy

---

## Cost Estimate

- **Vercel**: Free (Hobby plan)
- **Render**: Free tier (750 hours/month, spins down after inactivity)
- **MongoDB Atlas**: Free (M0 tier - 512MB storage)

**Total**: $0/month (Free tier)

---

## Next Steps

1. Set up automated scraping (optional):
   - Use Render Cron Jobs or external scheduler
   - Or run scraper manually when needed

2. Monitor your deployments:
   - Render: Check logs and metrics
   - Vercel: Check analytics and logs

3. Scale if needed:
   - Upgrade Render plan for always-on service
   - Upgrade MongoDB Atlas for more storage

---

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com

---

**Happy Deploying! 🚀**
