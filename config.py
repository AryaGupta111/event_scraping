"""
Configuration for the Events Scraper System
"""

import os

# MongoDB Configuration
# For MongoDB Atlas (Cloud):
# Replace the connection string below with your MongoDB Atlas connection string
# Example: mongodb+srv://admin:yourpassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0')

# IMPORTANT: After getting your MongoDB Atlas connection string:
# 1. Replace the MONGODB_URI above with your Atlas connection string
# 2. Make sure to replace <password> with your actual password
# 3. Keep the quotes around the connection string

DATABASE_NAME = 'crypto_events_db'
EVENTS_COLLECTION = 'events'
USER_COLLECTION = 'user'  # User-listed events (form submissions); images stored as URLs
# Note: Images are NOT stored in MongoDB - we use direct URLs from Luma CDN
# This saves database space and improves performance

# Scraping Configuration
SCRAPE_INTERVAL_HOURS = 24
BASE_URL = "https://lu.ma"
BASE_API_URL = "https://api2.luma.com"

# API Configuration
# Render provides PORT environment variable, fallback to 5000 for local development
API_PORT = int(os.getenv('PORT', 5000))
API_HOST = os.getenv('API_HOST', '0.0.0.0')

# Luma API Headers
API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en",
    "Origin": "https://lu.ma",
    "Referer": "https://lu.ma/crypto",
    "X-Luma-Client-Type": "luma-web",
}

# Crypto locations for scraping
CRYPTO_LOCATIONS = [
    {"name": "San Francisco, USA", "lat": 37.7749, "lng": -122.4194},
    {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060},
    {"name": "London, UK", "lat": 51.5074, "lng": -0.1278},
    {"name": "Berlin, Germany", "lat": 52.5200, "lng": 13.4050},
    {"name": "Singapore", "lat": 1.3521, "lng": 103.8198},
    {"name": "Tokyo, Japan", "lat": 35.6762, "lng": 139.6503},
    {"name": "Dubai, UAE", "lat": 25.2048, "lng": 55.2708},
    {"name": "Toronto, Canada", "lat": 43.6532, "lng": -79.3832},
    {"name": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
    {"name": "Hong Kong", "lat": 22.3193, "lng": 114.1694},
    {"name": "Mumbai, India", "lat": 19.0760, "lng": 72.8777},
    {"name": "Bangalore, India", "lat": 12.9716, "lng": 77.5946},
]

# Rate limiting
API_RATE_DELAY = 0.3
