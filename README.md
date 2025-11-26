# 🚀 Automated Hybrid Crypto Events Scraper

**Comprehensive automated system for discovering and monitoring crypto/web3 events globally**

## 🎯 What This Does

- **Discovers 400-500+ crypto events daily** across 40+ global cities
- **Runs automatically at 2:00 AM** every day
- **Prevents duplicates** - only new events are added
- **Combines API speed** (30 seconds) with **web scraping depth** 
- **Maintains Excel database** with comprehensive event details

## ⚡ Quick Start

1. **Setup (one time):**
   ```bash
   python3 setup_automation.py
   ```

2. **Test run now:**
   ```bash
   python3 automated_hybrid_scraper.py
   ```

3. **Start daily automation:**
   ```bash
   python3 scheduler.py
   ```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `automated_hybrid_scraper.py` | Main scraper (API + Web) |
| `scheduler.py` | Daily automation at 2:00 AM |
| `setup_automation.py` | One-time setup script |
| `luma_crypto_events_master.xlsx` | **YOUR RESULTS** (Excel database) |
| `scraper.log` | Execution logs |
| `scheduler.log` | Automation logs |

## 🎯 Key Features

### 🌍 **Global API Discovery**
- **40+ major crypto cities** (SF, NYC, London, Dubai, Tokyo, etc.)
- **Authenticated session** for best API access
- **~400+ events in 30 seconds**

### 🔍 **Enhanced Web Scraping**  
- **Targeted crypto categories** and searches
- **Quality filtering** with 60+ crypto keywords
- **Detailed event information**

### 🤖 **Smart Automation**
- **Daily execution at 2:00 AM**
- **Duplicate prevention** via event ID tracking
- **Comprehensive logging**
- **Email notifications** (optional)

### 📊 **Rich Data Collection**
Each event includes:
- Title, date, venue, organizer
- Attendee count, ticket information
- Event descriptions and images
- Geographic discovery location
- Source tracking (API vs web)

## 🛠️ Customization

### Update Schedule Time
Edit `scheduler.py`:
```python
SCHEDULE_TIME = "02:00"  # Change to your preferred time
```

### Refresh Authentication
Update your cookies in `automated_hybrid_scraper.py`:
```python
AUTHENTICATED_COOKIES = {
    'luma.auth-session-key': 'your-new-session-key',
    # ... other cookies
}
```

### Add Email Notifications
Configure in `scheduler.py`:
```python
ENABLE_EMAIL_NOTIFICATIONS = True
EMAIL_CONFIG = {
    "sender_email": "your_email@gmail.com",
    "recipient_email": "notifications@yourdomain.com"
}
```

## 📊 Expected Results

### **Daily Performance:**
- ⚡ **Runtime:** 30-60 seconds (API) + 2-5 minutes (web scraping)
- 🎯 **Discovery:** 400-500+ unique crypto events
- 🌍 **Coverage:** Global across major crypto hubs
- 📈 **Growth:** 20-50 new events daily (varies by crypto activity)

### **Data Quality:**
- ✅ **No duplicates** (smart ID-based deduplication)
- ✅ **Rich metadata** (attendees, venues, organizers)
- ✅ **Structured format** (Excel with consistent columns)
- ✅ **Source tracking** (know whether API or web discovered each event)

## 🔧 Troubleshooting

### **No new events found:**
- Update cookies in `automated_hybrid_scraper.py`
- Check internet connection
- Review logs in `scraper.log`

### **Scheduler not running:**
- Ensure computer stays on overnight
- Check `scheduler.log` for errors
- Test with: `python3 scheduler.py --run-now`

### **Excel file errors:**
- Ensure Excel/LibreOffice is not keeping file open
- Check file permissions
- Backup existing file before runs

## 📈 Growth Over Time

**Week 1:** ~400 initial events  
**Week 2:** +100-200 new events  
**Month 1:** 1,000+ comprehensive event database  
**Month 3:** 2,500+ events with historical coverage

## 🎉 Success Metrics

After setup, you should see:

```
📊 Final Statistics:
   • Runtime: 45.2 seconds  
   • API calls: 40
   • New API events: 387
   • New web events: 12
   • Total new events: 399
   • Duplicates prevented: 23
💾 Results in: luma_crypto_events_master.xlsx
```

## 🔄 Daily Workflow

1. **2:00 AM:** Scheduler automatically starts scraper
2. **2:01 AM:** API discovers events across 40+ cities  
3. **2:02 AM:** Web scraping adds detailed events
4. **2:03 AM:** Deduplication and Excel database update
5. **2:04 AM:** Logging and optional email notification
6. **Done:** New crypto events ready for your review!

---

**🎯 Built for comprehensive crypto events monitoring with zero manual effort!**

**Questions or issues?** Check the log files or run components manually for debugging.