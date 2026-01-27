# 🚀 How to Run the System

## Quick Start (2 Steps)

### **Step 1: Start the API Server**

**Option A - Double-click:**
```
start_api_server.bat
```

**Option B - Command line:**
```bash
python api_server.py
```

**✅ You should see:**
```
╔══════════════════════════════════════════════════════════╗
║         🚀 Crypto Events API Server                     ║
╚══════════════════════════════════════════════════════════╝

📡 Server running at: http://localhost:5000
```

**⚠️ IMPORTANT: Keep this window open!**

---

### **Step 2: Open the Webpage**

1. Open your browser (Chrome, Firefox, Edge, etc.)
2. Navigate to your project folder
3. Double-click `events_api.html`

Or drag `events_api.html` into your browser.

**✅ You should see:**
- Events displayed in a grid
- Images loading from Luma CDN
- White background with blue accents

---

## Troubleshooting

### ❌ Error: "ERR_CONNECTION_REFUSED"

**Problem:** API server is not running

**Solution:**
1. Make sure you ran Step 1 (start API server)
2. Check the server window is still open
3. Look for "Server running at: http://localhost:5000"
4. If server stopped, restart it

---

### ❌ Error: "Failed to fetch"

**Problem:** API server stopped or crashed

**Solution:**
1. Close the server window
2. Run `start_api_server.bat` again
3. Wait for "Server running" message
4. Refresh browser (Ctrl+R)

---

### ❌ Error: "Port 5000 already in use"

**Problem:** Another program is using port 5000

**Solution:**
1. Open `config.py`
2. Change line: `API_PORT = 5000` to `API_PORT = 8080`
3. Save file
4. Restart API server
5. Refresh browser

---

### ❌ No events showing

**Problem:** Database is empty

**Solution:**
```bash
python scraper_mongodb.py
```

Wait for scraping to complete, then refresh browser.

---

### ❌ Images not loading

**Problem:** Image URLs missing or CDN issue

**Solution:**
1. Check if API server is running
2. Open browser console (F12)
3. Look for specific errors
4. Try hard refresh: Ctrl+Shift+R

---

## Complete Setup (First Time)

If you haven't set up the system yet:

```bash
# Run complete setup
python setup_and_run.py
```

This will:
1. Check dependencies
2. Connect to MongoDB
3. Scrape events (if needed)
4. Start API server

---

## Daily Workflow

### Morning:
```bash
# Start the server
python api_server.py
```

### Use:
- Open `events_api.html` in browser
- Browse events
- Use search and filters

### Evening:
- Press Ctrl+C in server window to stop

---

## File Locations

```
D:\events_scrapper\
├── start_api_server.bat    ← Double-click to start server
├── api_server.py            ← Or run this directly
└── events_api.html          ← Open this in browser
```

---

## Quick Commands

```bash
# Start API server
python api_server.py

# Or use batch file
start_api_server.bat

# Check system status
python check_images.py

# Scrape new events
python scraper_mongodb.py

# Complete setup
python setup_and_run.py
```

---

## Verification Checklist

Before opening the webpage, verify:

- [ ] API server is running
- [ ] You see "Server running at: http://localhost:5000"
- [ ] Server window is still open (not closed)
- [ ] No error messages in server window

Then:

- [ ] Open `events_api.html` in browser
- [ ] Events are displayed
- [ ] Images are loading
- [ ] No errors in browser console (F12)

---

## Common Mistakes

### ❌ Closing the server window
**Problem:** Server stops when you close the window

**Solution:** Keep the server window open while using the webpage

### ❌ Not starting the server
**Problem:** Opening webpage before starting server

**Solution:** Always start server first (Step 1), then open webpage (Step 2)

### ❌ Wrong port
**Problem:** Server running on different port

**Solution:** Check server message for actual port number

---

## Server Status

To check if server is running:

1. Open browser
2. Go to: http://localhost:5000/api/health
3. You should see: `{"status":"healthy"}`

If you see an error, the server is not running.

---

## Need Help?

1. **Check server is running:** Look for "Server running" message
2. **Check browser console:** Press F12 in browser
3. **Run diagnostics:** `python check_images.py`
4. **Restart everything:** Close server, run `start_api_server.bat`, refresh browser

---

## Summary

**Two simple steps:**

1. **Start server:** `start_api_server.bat` (keep window open)
2. **Open webpage:** Double-click `events_api.html`

**That's it!** 🎉
