"""
Automated Scheduler Service
Runs scraper every 24 hours
"""

import schedule
import time
import logging
from datetime import datetime
from scraper_mongodb import main as run_scraper
from config import SCRAPE_INTERVAL_HOURS

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

def run_scheduler():
    """Run the scheduler service"""
    logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║         ⏰ Automated Scraper Scheduler                   ║
╚══════════════════════════════════════════════════════════╝

📅 Schedule: Every {SCRAPE_INTERVAL_HOURS} hours
🕐 Next run: {schedule.next_run()}

Running initial scrape now...
    """)
    
    # Run immediately on start
    scheduled_scrape()
    
    # Schedule for every 24 hours
    schedule.every(SCRAPE_INTERVAL_HOURS).hours.do(scheduled_scrape)
    
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
