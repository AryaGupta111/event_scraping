"""
MongoDB Database Manager
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timezone
import logging
from config import MONGODB_URI, DATABASE_NAME, EVENTS_COLLECTION, USER_COLLECTION

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DATABASE_NAME]
            self.events = self.db[EVENTS_COLLECTION]
            self.user_listed = self.db[USER_COLLECTION]
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        # Events indexes
        self.events.create_index([("external_id", ASCENDING)], unique=True)
        self.events.create_index([("date_time", DESCENDING)])
        self.events.create_index([("scraped_at", DESCENDING)])
        self.events.create_index([("title", "text"), ("description", "text")])
        self.user_listed.create_index([("listed_at", -1)])
        
        logger.info("✅ Database indexes created")
    
    def save_event(self, event_data):
        """Save or update an event"""
        try:
            event_data['updated_at'] = datetime.now(timezone.utc)
            
            result = self.events.update_one(
                {'external_id': event_data['external_id']},
                {'$set': event_data},
                upsert=True
            )
            
            return result.upserted_id or result.modified_count > 0
        except Exception as e:
            logger.error(f"Error saving event {event_data.get('external_id')}: {e}")
            return False
    
    def get_all_events(self, filters=None, limit=None, skip=0):
        """Get all events with optional filters"""
        try:
            query = filters or {}
            cursor = self.events.find(query).sort('date_time', DESCENDING)
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            events = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for event in events:
                event['_id'] = str(event['_id'])
            
            return events
        except Exception as e:
            logger.error(f"Error retrieving events: {e}")
            return []
    
    def get_event_by_id(self, external_id):
        """Get a single event by external_id"""
        try:
            event = self.events.find_one({'external_id': external_id})
            if event:
                event['_id'] = str(event['_id'])
            return event
        except Exception as e:
            logger.error(f"Error retrieving event {external_id}: {e}")
            return None
    
    def count_events(self, filters=None):
        """Count events with optional filters"""
        try:
            query = filters or {}
            return self.events.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting events: {e}")
            return 0
    
    def delete_old_events(self, days=90):
        """Delete events older than specified days"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            result = self.events.delete_many({
                'scraped_at': {'$lt': cutoff_date}
            })
            logger.info(f"🗑️  Deleted {result.deleted_count} old events")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting old events: {e}")
            return 0
    
    def save_user_listed_event(self, event_data):
        """Save a user-listed event to the user collection. Images stored as URLs."""
        try:
            event_data['listed_at'] = datetime.now(timezone.utc).isoformat()
            event_data['source'] = 'user_listed'
            if not event_data.get('external_id'):
                import uuid
                event_data['external_id'] = 'user-' + str(uuid.uuid4())[:12]
            self.user_listed.insert_one(event_data)
            return event_data.get('external_id')
        except Exception as e:
            logger.error(f"Error saving user-listed event: {e}")
            return None
    
    def get_stats(self):
        """Get database statistics"""
        try:
            total_events = self.events.count_documents({})
            
            # Count by status
            now = datetime.now(timezone.utc)
            upcoming = self.events.count_documents({
                'date_time': {'$gt': now.isoformat()}
            })
            
            # Count events with images
            events_with_images = self.events.count_documents({
                'image_url': {'$exists': True, '$ne': None, '$ne': 'null', '$ne': 'None'}
            })
            
            return {
                'total_events': total_events,
                'events_with_images': events_with_images,
                'upcoming_events': upcoming,
                'database_name': DATABASE_NAME,
                'storage_method': 'Direct URLs (no image storage in DB)'
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        logger.info("🔌 MongoDB connection closed")
