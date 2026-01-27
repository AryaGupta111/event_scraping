"""
Check system status and image URLs
"""

from database import DatabaseManager
import requests

print("🔍 Checking System Status")
print("=" * 60)

# Check database
db = DatabaseManager()

# Get stats
stats = db.get_stats()
print(f"\n📊 Database Stats:")
print(f"   Total Events: {stats.get('total_events', 0)}")
print(f"   Events with Images: {stats.get('events_with_images', 0)}")
print(f"   Upcoming Events: {stats.get('upcoming_events', 0)}")
print(f"   Storage Method: {stats.get('storage_method', 'N/A')}")

# Get a few events
events = db.get_all_events(limit=5)
print(f"\n📋 Sample Events:")

for i, event in enumerate(events, 1):
    event_id = event.get('external_id')
    title = event.get('title', 'Untitled')[:50]
    image_url = event.get('image_url')
    
    has_image = "✅" if image_url and image_url not in ['null', 'None', None] else "❌"
    
    print(f"\n   {i}. {has_image} {title}")
    print(f"      ID: {event_id}")
    
    if image_url and image_url not in ['null', 'None', None]:
        print(f"      Image URL: {image_url[:80]}...")
    else:
        print(f"      Image URL: None")

print("\n" + "=" * 60)
print("🌐 Testing API Server")
print("=" * 60)

# Test if API server is running
try:
    response = requests.get('http://localhost:5000/api/health', timeout=2)
    if response.status_code == 200:
        print("✅ API Server is running")
        
        # Test stats endpoint
        stats_response = requests.get('http://localhost:5000/api/stats', timeout=5)
        if stats_response.status_code == 200:
            api_stats = stats_response.json()
            print(f"\n📊 API Stats:")
            if api_stats.get('success'):
                for key, value in api_stats.get('stats', {}).items():
                    print(f"   {key}: {value}")
    else:
        print(f"⚠️  API Server responded with status: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ API Server is NOT running!")
    print("\n💡 Solution:")
    print("   Run: python api_server.py")
    print("   Or: python setup_and_run.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("📝 Summary")
print("=" * 60)

total = stats.get('total_events', 0)
with_images = stats.get('events_with_images', 0)

if total == 0:
    print("\n❌ NO EVENTS IN DATABASE")
    print("\n💡 Solution:")
    print("   Run: python setup_and_run.py")
elif with_images == 0:
    print(f"\n⚠️  NO IMAGE URLS: {total} events but no image URLs")
    print("\n💡 Solution:")
    print("   Run: python scraper_mongodb.py")
elif with_images < total:
    print(f"\n⚠️  PARTIAL IMAGES: {with_images} of {total} events have image URLs")
    print("\n💡 This is normal - not all events have images")
else:
    print(f"\n✅ ALL GOOD: {with_images} of {total} events have image URLs")

print("\n💡 Image Storage:")
print("   Images are loaded directly from Luma CDN")
print("   No images stored in MongoDB (saves space!)")
print("   Frontend loads images from original URLs")

db.close()

input("\nPress Enter to exit...")
