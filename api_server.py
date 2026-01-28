"""
Flask API Server for Events
Serves events and images from MongoDB
"""

from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
from database import DatabaseManager
from datetime import datetime, timezone
import io
import logging
from config import API_PORT, API_HOST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce MongoDB logging verbosity
logging.getLogger('pymongo').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize database
db = DatabaseManager()

def clean_event_data(event):
    """Remove internal/sensitive fields from event data"""
    # Fields to keep (whitelist approach - more secure)
    # Removed: ticket_url, image_url (hidden from public API response)
    allowed_fields = [
        'external_id', 'title', 'date_time', 'end_time', 'venue',
        'organizer', 'description', 'category_tags',
        'guest_count', 'ticket_count', 'timezone',
        'event_type', 'discovery_location'
    ]
    
    # Create clean event dict with only allowed fields
    clean_event = {k: v for k, v in event.items() if k in allowed_fields}
    
    return clean_event

def internal_clean_event_data(event):
    """Remove only MongoDB internal fields, keep URLs for frontend"""
    # Remove only MongoDB internal fields
    internal_fields = ['_id', 'scraped_at', 'updated_at', 'source']
    
    # Create clean event dict
    clean_event = {k: v for k, v in event.items() if k not in internal_fields}
    
    return clean_event

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filtering (PUBLIC - URLs hidden)"""
    try:
        # Get query parameters with default limit
        limit = request.args.get('limit', 100, type=int)  # Default 100 events
        skip = request.args.get('skip', 0, type=int)
        search = request.args.get('search', '')
        location = request.args.get('location', '')
        status = request.args.get('status', '')
        
        # Enforce maximum limit for security
        if limit > 500:
            limit = 500
        
        # Build filters
        filters = {}
        
        if search:
            filters['$text'] = {'$search': search}
        
        if location:
            filters['venue'] = {'$regex': location, '$options': 'i'}
        
        if status:
            now = datetime.now().isoformat()
            if status == 'upcoming':
                filters['date_time'] = {'$gt': now}
            elif status == 'ended':
                filters['end_time'] = {'$lt': now}
            elif status == 'ongoing':
                filters['$and'] = [
                    {'date_time': {'$lte': now}},
                    {'end_time': {'$gte': now}}
                ]
        
        # Get events
        events = db.get_all_events(filters=filters, limit=limit, skip=skip)
        total = db.count_events(filters=filters)
        
        # Clean events data - remove internal fields AND URLs (public API)
        clean_events = [clean_event_data(event) for event in events]
        
        return jsonify({
            'success': True,
            'events': clean_events,
            'total': total,
            'count': len(clean_events)
        })
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/internal/events', methods=['GET'])
def get_internal_events():
    """Get all events with URLs (INTERNAL - for frontend use only)"""
    try:
        # Get query parameters with default limit
        limit = request.args.get('limit', type=int)
        skip = request.args.get('skip', 0, type=int)
        search = request.args.get('search', '')
        location = request.args.get('location', '')
        status = request.args.get('status', '')
        
        # Build filters
        filters = {}
        
        if search:
            filters['$text'] = {'$search': search}
        
        if location:
            filters['venue'] = {'$regex': location, '$options': 'i'}
        
        if status:
            now = datetime.now().isoformat()
            if status == 'upcoming':
                filters['date_time'] = {'$gt': now}
            elif status == 'ended':
                filters['end_time'] = {'$lt': now}
            elif status == 'ongoing':
                filters['$and'] = [
                    {'date_time': {'$lte': now}},
                    {'end_time': {'$gte': now}}
                ]
        
        # Get events
        events = db.get_all_events(filters=filters, limit=limit, skip=skip)
        total = db.count_events(filters=filters)
        
        # Clean events data - remove only MongoDB internal fields, keep URLs
        clean_events = [internal_clean_event_data(event) for event in events]
        
        return jsonify({
            'success': True,
            'events': clean_events,
            'total': total,
            'count': len(clean_events)
        })
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get a single event by ID"""
    try:
        event = db.get_event_by_id(event_id)
        
        if event:
            # Clean the event data
            clean_event = clean_event_data(event)
            return jsonify({'success': True, 'event': clean_event})
        else:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/images/<event_id>', methods=['GET'])
def get_image(event_id):
    """Get image URL for an event (returns URL, not image data)"""
    try:
        event = db.get_event_by_id(event_id)
        
        if event and event.get('image_url'):
            # Return the image URL so frontend can load it directly
            return jsonify({
                'success': True,
                'image_url': event['image_url']
            })
        else:
            # Return placeholder if no image
            return jsonify({
                'success': False,
                'image_url': None
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting image URL for {event_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/list-event', methods=['POST'])
def list_event():
    """Save user-listed event to MongoDB user collection. Images as URLs."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON body'}), 400
        
        title = (data.get('title') or '').strip()
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Build event doc; store image as URL only
        event_data = {
            'title': title,
            'description': (data.get('description') or '').strip() or None,
            'venue': (data.get('venue') or '').strip() or None,
            'date_time': (data.get('date_time') or '').strip() or None,
            'end_time': (data.get('end_time') or '').strip() or None,
            'image_url': (data.get('image_url') or '').strip() or None,
            'category_tags': (data.get('category_tags') or '').strip() or None,
            'organizer': (data.get('organizer') or '').strip() or None,
            'ticket_url': (data.get('ticket_url') or '').strip() or None,
            'event_type': (data.get('event_type') or '').strip() or None,
            # Extended structured fields from multi-step form (all optional)
            'organizer_details': data.get('organizer_details') or None,
            'tickets': data.get('tickets') or [],
            'sponsors': data.get('sponsors') or [],
            'partners': data.get('partners') or [],
            'faqs': data.get('faqs') or [],
            'contents': data.get('contents') or [],
        }
        
        eid = db.save_user_listed_event(event_data)
        if eid:
            # Also insert into main events collection so it appears in listings
            tags = event_data['category_tags']
            if not tags:
                base_tags = ['crypto', 'web3', 'blockchain']
                if event_data.get('event_type'):
                    base_tags.append(event_data['event_type'])
                tags = ','.join(base_tags)

            event_doc = {
                'external_id': eid,
                'event_slug': None,
                'title': event_data['title'],
                'date_time': event_data['date_time'],
                'end_time': event_data['end_time'],
                'venue': event_data['venue'],
                'organizer': event_data['organizer'],
                'description': event_data['description'],
                'category_tags': tags,
                'ticket_url': event_data['ticket_url'],
                'image_url': event_data['image_url'],
                'guest_count': 0,
                'ticket_count': 0,
                'discovery_location': None,
                'timezone': None,
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'source': 'user_listed'
            }
            db.save_event(event_doc)

            return jsonify({'success': True, 'external_id': eid})
        return jsonify({'success': False, 'error': 'Failed to save event'}), 500
    except Exception as e:
        logger.error(f"Error in list-event: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Crypto Events API',
        'version': '1.0.0',
        'endpoints': {
            '/api/events': 'Get all events (PUBLIC - URLs hidden)',
            '/api/internal/events': 'Get all events with URLs (INTERNAL - for frontend)',
            '/api/events/<id>': 'Get single event (PUBLIC)',
            '/api/images/<id>': 'Get event image URL',
            '/api/user/list-event': 'POST: Submit user-listed event',
            '/api/stats': 'Get database statistics',
            '/api/health': 'Health check'
        }
    })

if __name__ == '__main__':
    print("\n" + "=" * 60)
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
    
    try:
        app.run(host=API_HOST, port=API_PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        input("\nPress Enter to exit...")
