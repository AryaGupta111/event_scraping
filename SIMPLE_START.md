# 🚀 One Command Setup

## Quick Start

### **Option 1: Double-Click (Easiest)**
Just double-click: **`RUN.bat`**

### **Option 2: Command Line**
```cmd
python setup_and_run.py
```

---

## What It Does

This single command will:

1. ✅ **Check Dependencies** - Installs missing Python packages
2. ✅ **Connect to MongoDB** - Verifies Atlas connection
3. ✅ **Scrape Events** - Gets latest events from Luma (if needed)
4. ✅ **Download Images** - Downloads all event images (if needed)
5. ✅ **Start API Server** - Launches the backend server

---

## After Running

1. Wait for the message: **"Press Enter to start the API server..."**
2. Press Enter
3. Server will start (keep the window open!)
4. Open **`events_api.html`** in your browser
5. See your events with images! 🎉

---

## First Time Setup

Before running, make sure you have:

- ✅ Python installed
- ✅ MongoDB Atlas account created
- ✅ Connection string updated in `config.py`

**MongoDB Atlas Setup:**
1. Go to: https://cloud.mongodb.com/
2. Create free cluster (M0)
3. Create database user
4. Allow network access (0.0.0.0/0)
5. Copy connection string
6. Update `config.py` line 11 with your connection string

---

## Daily Usage

After first setup, just run:
```cmd
python setup_and_run.py
```

Or double-click: **`RUN.bat`**

The system will:
- Skip scraping if events exist (unless you choose to re-scrape)
- Skip image download if images exist
- Start the API server immediately

---

## Stopping the Server

Press **Ctrl+C** in the command window

---

## Troubleshooting

### "MongoDB connection failed"
- Check `config.py` has correct connection string
- Verify Network Access in MongoDB Atlas
- Check username/password

### "No images showing"
- Make sure API server is running
- Refresh browser with Ctrl+Shift+R
- Check browser console (F12) for errors

### "Dependencies failed to install"
- Run Command Prompt as Administrator
- Or use: `python -m pip install --user <package>`

---

## Files Overview

- **`RUN.bat`** - Double-click to start everything
- **`setup_and_run.py`** - Main setup script
- **`config.py`** - Configuration (MongoDB connection)
- **`events_api.html`** - Open this in browser
- **`api_server.py`** - Backend server (auto-started)

---

## System Architecture

```
RUN.bat
   ↓
setup_and_run.py
   ↓
1. Install dependencies
2. Check MongoDB
3. Scrape events → MongoDB
4. Download images → MongoDB
5. Start api_server.py
   ↓
Open events_api.html in browser
   ↓
See events with images! 🎉
```

---

## Need Help?

Run the diagnostic:
```cmd
python check_images.py
```

This shows:
- How many events in database
- How many images stored
- If API server is running
- What's wrong (if anything)

---

**🎉 That's it! One command to rule them all!**
