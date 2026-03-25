"""
MongoDB-based Event Scraper
Scrapes events and stores them in MongoDB with images
"""

import requests
import time
import logging
from datetime import datetime, timezone
from dateutil import parser as dateparser
from database import DatabaseManager
from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Reduce MongoDB logging verbosity
logging.getLogger('pymongo').setLevel(logging.WARNING)

class MongoDBScraper:
    def __init__(self):
        self.db = DatabaseManager()
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)
        self.stats = {
            'events_scraped': 0,
            'events_saved': 0,
            'errors': 0
        }
    
    def scrape_all_events(self):
        """Scrape events from all categories and locations"""
        logger.info("🚀 Starting event scraping...")
        logger.info(f"📂 Categories: {len(EVENT_CATEGORIES)}")
        logger.info(f"📍 Locations: {len(SCRAPING_LOCATIONS)}")
        
        for category in EVENT_CATEGORIES:
            logger.info(f"\n{'='*60}")
            logger.info(f"📂 Category: {category['name']} (slug: {category['slug']})")
            logger.info(f"{'='*60}")
            
            for idx, location in enumerate(SCRAPING_LOCATIONS, 1):
                try:
                    logger.info(f"[{idx}/{len(SCRAPING_LOCATIONS)}] 🌍 {location['name']}")
                    self._scrape_location(location, category)
                    time.sleep(API_RATE_DELAY)
                except Exception as e:
                    logger.error(f"❌ Error scraping {location['name']}: {e}")
                    self.stats['errors'] += 1
        
        logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║                  📊 SCRAPING SUMMARY                     ║
╚══════════════════════════════════════════════════════════╝

✅ Events Scraped: {self.stats['events_scraped']}
💾 Events Saved: {self.stats['events_saved']}
🔗 Image URLs Stored: {self.stats['events_scraped']}
❌ Errors: {self.stats['errors']}
        """)
        
        return self.stats
    
    def _scrape_location(self, location, category):
        """Scrape events for a specific location and category"""
        try:
            response = self.session.get(
                f"{BASE_API_URL}/discover/get-paginated-events",
                params={
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "pagination_limit": 100,
                    "slug": category["slug"]
                }
            )
            response.raise_for_status()
            
            data = response.json()
            entries = data.get("entries", [])
            
            logger.info(f"   📊 Found {len(entries)} events")
            
            for entry in entries:
                self._process_event(entry, location["name"], category)
                
        except Exception as e:
            logger.error(f"Error fetching events for {location['name']}: {e}")
            raise
    
    def _process_event(self, entry, location_name, category):
        """Process and save a single event"""
        try:
            event_data = entry.get("event", {})
            event_id = entry.get("api_id")
            
            if not event_id:
                return
            
            # Parse event data
            parsed_event = self._parse_event_data(entry, location_name, category)
            
            if not parsed_event:
                return
            
            # Check if event already exists
            existing_event = self.db.get_event_by_id(event_id)
            
            # Save event to database
            if self.db.save_event(parsed_event):
                if not existing_event:
                    self.stats['events_saved'] += 1
                    logger.info(f"   ✅ Saved: {parsed_event['title'][:50]}")
            
            self.stats['events_scraped'] += 1
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            self.stats['errors'] += 1
    
    def _parse_event_data(self, entry, location_name, category):
        """Parse event data from API response"""
        try:
            event_data = entry.get("event", {})
            event_id = entry.get("api_id")
            
            # Extract venue
            geo_data = event_data.get("geo_address_info", {})
            venue_parts = []
            if geo_data.get("address"):
                venue_parts.append(str(geo_data["address"]))
            if geo_data.get("city_state"):
                venue_parts.append(str(geo_data["city_state"]))
            if geo_data.get("country"):
                venue_parts.append(str(geo_data["country"]))
            venue = ", ".join(venue_parts) if venue_parts else None
            
            # Extract organizer
            hosts = entry.get("hosts", [])
            organizer_names = [host.get("name") for host in hosts if host.get("name")]
            organizer = ", ".join(organizer_names) if organizer_names else None
            
            # Extract image URL
            # Try multiple possible locations for image URL
            image_url = None
            
            # First try: event.cover_url (most common)
            if event_data.get("cover_url"):
                image_url = event_data.get("cover_url")
            # Second try: cover_image object
            elif entry.get("cover_image", {}).get("url"):
                image_url = entry.get("cover_image", {}).get("url")
            # Third try: calendar cover image
            elif entry.get("calendar", {}).get("cover_image_url"):
                image_url = entry.get("calendar", {}).get("cover_image_url")
            # Fourth try: calendar avatar
            elif entry.get("calendar", {}).get("avatar_url"):
                image_url = entry.get("calendar", {}).get("avatar_url")
            
            # Build event URL
            slug = (event_data.get("url") or "").strip("/")
            event_url = f"{BASE_URL}/{slug}" if slug else f"{BASE_URL}/{event_id}"
            
            # Extract event type from event data
            event_type = event_data.get("event_type") or event_data.get("meeting_type")
            
            # Parse dates
            start_iso = self._normalize_datetime(entry.get("start_at"))
            end_iso = self._normalize_datetime(entry.get("end_at"))
            
            return {
                "external_id": event_id,
                "event_slug": slug or None,
                "title": event_data.get("name"),
                "date_time": start_iso,
                "end_time": end_iso,
                "venue": venue,
                "organizer": organizer,
                "description": event_data.get("description"),
                "category_tags": category["tags"],
                "event_type": event_type,
                "ticket_url": event_url,
                "image_url": image_url,
                "guest_count": entry.get("guest_count", 0),
                "ticket_count": entry.get("ticket_count", 0),
                "discovery_location": location_name,
                "timezone": event_data.get("timezone"),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source": f"api-{category['slug']}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing event data: {e}")
            return None
    
    def _normalize_datetime(self, dt_text):
        """Normalize datetime string"""
        if not dt_text:
            return None
        try:
            dt = dateparser.parse(dt_text)
            if dt and not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat() if dt else dt_text.strip()
        except Exception:
            return dt_text.strip() if dt_text else None

def main():
    """Main scraping function"""
    scraper = MongoDBScraper()
    try:
        stats = scraper.scrape_all_events()
        return stats
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return None
    finally:
        scraper.db.close()

if __name__ == "__main__":
    main()
