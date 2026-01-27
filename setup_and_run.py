"""
Complete Setup and Run Script
One command to set up everything and start the system
"""

import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_dependencies():
    """Check if required packages are installed"""
    print_header("📦 Step 1: Checking Dependencies")
    
    missing = []
    packages = [
        ('pymongo', 'pymongo'),
        ('flask', 'flask'),
        ('flask_cors', 'flask-cors'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('dateutil', 'python-dateutil'),
        ('schedule', 'schedule'),
        ('PIL', 'Pillow')
    ]
    
    for module, package in packages:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\n💡 Installing missing packages...")
        
        for package in missing:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', package], 
                             check=True, capture_output=True)
                print(f"  ✅ Installed {package}")
            except:
                print(f"  ❌ Failed to install {package}")
                return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_mongodb():
    """Check MongoDB connection"""
    print_header("🔍 Step 2: Checking MongoDB Connection")
    
    try:
        from pymongo import MongoClient
        from config import MONGODB_URI
        
        print(f"📡 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
        client.server_info()
        print("✅ MongoDB Atlas connected!")
        
        # Check database stats
        from database import DatabaseManager
        db = DatabaseManager()
        stats = db.get_stats()
        
        print(f"\n📊 Current Database Status:")
        print(f"   Events: {stats.get('total_events', 0)}")
        print(f"   Images: {stats.get('total_images', 0)}")
        
        db.close()
        client.close()
        return True, stats
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n💡 Please check:")
        print("   1. MongoDB Atlas connection string in config.py")
        print("   2. Network Access allows 0.0.0.0/0")
        print("   3. Username and password are correct")
        return False, {}

def scrape_events():
    """Scrape events from Luma"""
    print_header("🌐 Step 3: Scraping Events")
    
    try:
        from scraper_mongodb import main
        print("⏳ Scraping events from Luma (this takes 2-3 minutes)...")
        stats = main()
        
        if stats:
            print(f"\n✅ Scraping completed!")
            print(f"   Events: {stats['events_scraped']}")
            print(f"   Saved: {stats['events_saved']}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return False

def start_api_server():
    """Start the API server"""
    print_header("🚀 Step 4: Starting API Server")
    
    print("📡 Starting Flask API server...")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        # Import Flask app
        from api_server import app, API_HOST, API_PORT
        
        print("=" * 60)
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         🚀 Crypto Events API Server                     ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print("=" * 60)
        print(f"\n📡 Server running at: http://localhost:{API_PORT}")
        print(f"📄 API Docs: http://localhost:{API_PORT}/")
        print(f"🔍 Events: http://localhost:{API_PORT}/api/events")
        print(f"📊 Stats: http://localhost:{API_PORT}/api/stats")
        print("\n⏹️  Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        # Run the Flask app (this blocks until Ctrl+C)
        app.run(host=API_HOST, port=API_PORT, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main setup and run function"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🚀 Crypto Events System - Complete Setup        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed at dependency check")
        input("\nPress Enter to exit...")
        return False
    
    # Step 2: Check MongoDB
    connected, stats = check_mongodb()
    if not connected:
        print("\n❌ Setup failed at MongoDB connection")
        input("\nPress Enter to exit...")
        return False
    
    # Step 3: Scrape events (if needed)
    if stats.get('total_events', 0) == 0:
        print("\n💡 No events in database, scraping now...")
        if not scrape_events():
            print("\n⚠️  Scraping failed, but continuing...")
    else:
        print(f"\n✅ Database already has {stats.get('total_events')} events")
        
        # Ask if user wants to re-scrape
        response = input("\n❓ Do you want to re-scrape events? (y/n): ").lower()
        if response == 'y':
            scrape_events()
    
    # Step 4: Start API server
    print_header("✅ Setup Complete!")
    print("📊 System Status:")
    
    # Get final stats
    from database import DatabaseManager
    db = DatabaseManager()
    final_stats = db.get_stats()
    db.close()
    
    print(f"   Events: {final_stats.get('total_events', 0)}")
    print(f"   Events with Images: {final_stats.get('events_with_images', 0)}")
    print(f"   Database: {final_stats.get('database_name', 'N/A')}")
    print(f"   Storage: {final_stats.get('storage_method', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("🌐 Next Steps:")
    print("=" * 60)
    print("\n1. API Server will start now")
    print("2. Open events_api.html in your browser")
    print("3. Images load directly from Luma CDN (no download needed!)")
    print("\n⏹️  Press Ctrl+C to stop the server anytime")
    
    input("\nPress Enter to start the API server...")
    
    # Start the server
    start_api_server()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")
