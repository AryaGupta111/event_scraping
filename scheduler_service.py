"""
Automated Scheduler Service
Runs scraper every 24 hours and cleans up ended events daily
"""

import schedule
import time
import logging
from datetime import datetime
from scraper_mongodb import main as run_scraper
from database import DatabaseManager
from config import SCRAPE_INTERVAL_HOURS, CLEANUP_GRACE_DAYS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def scheduled_scrape():
    """Run the scraper"""
    logger.info(f"⏰ Scheduled scrape started at {datetime.now()}")
    try:
        stats = run_scraper()
        if stats:
            logger.info(f"✅ Scrape completed: {stats['events_saved']} events saved")
        else:
            logger.error("❌ Scrape failed")
    except Exception as e:
        logger.error(f"❌ Scrape error: {e}")

def scheduled_cleanup():
    """Clean up ended events to save database storage"""
    logger.info(f"🧹 Scheduled cleanup started at {datetime.now()}")
    try:
        db = DatabaseManager()
        # Delete events that ended more than CLEANUP_GRACE_DAYS ago
        deleted_count = db.delete_ended_events(grace_days=CLEANUP_GRACE_DAYS)
        db.close()
        
        if deleted_count > 0:
            logger.info(f"✅ Cleanup completed: {deleted_count} ended events removed")
        else:
            logger.info("✅ Cleanup completed: No events to remove")
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")

def run_scheduler():
    """Run the scheduler service"""
    logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║         ⏰ Automated Scraper & Cleanup Scheduler         ║
╚══════════════════════════════════════════════════════════╝

📅 Scraping Schedule: Every {SCRAPE_INTERVAL_HOURS} hours
🧹 Cleanup Schedule: Daily at 02:00 AM
🕐 Next scrape: {schedule.next_run()}

Running initial scrape now...
    """)
    
    # Run scrape immediately on start
    scheduled_scrape()
    
    # Run cleanup immediately on start
    scheduled_cleanup()
    
    # Schedule scraping every 24 hours
    schedule.every(SCRAPE_INTERVAL_HOURS).hours.do(scheduled_scrape)
    
    # Schedule cleanup daily at 2 AM
    schedule.every().day.at("02:00").do(scheduled_cleanup)
    
    logger.info(f"✅ Scheduler started. Next run: {schedule.next_run()}")
    
    # Keep running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n🛑 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
