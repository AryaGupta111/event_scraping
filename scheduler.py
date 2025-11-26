#!/usr/bin/env python3
"""
⏰ AUTOMATED SCHEDULER for Hybrid Crypto Events Scraper
Runs daily at 2:00 AM and manages execution logging
"""

import schedule
import time
import subprocess
import logging
import smtplib
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sys
import os

# ============= CONFIGURATION =============
SCRAPER_SCRIPT = "automated_hybrid_scraper.py"
SCHEDULE_TIME = "02:00"  # 2:00 AM
LOG_FILE = "scheduler.log"

# Email notifications (optional - configure if desired)
ENABLE_EMAIL_NOTIFICATIONS = False
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",  # Use app password for Gmail
    "recipient_email": "your_email@gmail.com"
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scheduler")

class ScraperScheduler:
    def __init__(self):
        self.last_run_stats = {}
        self.total_runs = 0
        self.successful_runs = 0
        
    def run_scraper(self):
        """Execute the hybrid scraper and handle results."""
        run_start = datetime.now()
        logger.info(f"🚀 Starting scheduled scraper run #{self.total_runs + 1}")
        
        try:
            # Execute the scraper script
            result = subprocess.run(
                [sys.executable, SCRAPER_SCRIPT],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                # Success
                self.successful_runs += 1
                self.total_runs += 1
                
                logger.info("✅ Scraper completed successfully!")
                logger.info(f"📊 Success rate: {self.successful_runs}/{self.total_runs} ({(self.successful_runs/self.total_runs)*100:.1f}%)")
                
                # Log output
                if result.stdout:
                    logger.info("Scraper output:")
                    for line in result.stdout.strip().split('\n')[-10:]:  # Last 10 lines
                        logger.info(f"   {line}")
                
                # Parse statistics if available
                self.parse_scraper_output(result.stdout)
                
                # Send success notification
                if ENABLE_EMAIL_NOTIFICATIONS:
                    self.send_notification(
                        subject="✅ Crypto Events Scraper - Success",
                        body=f"Scraper completed successfully at {run_start}\n\nStats: {self.last_run_stats}"
                    )
                    
            else:
                # Failure
                self.total_runs += 1
                logger.error(f"❌ Scraper failed with return code {result.returncode}")
                
                if result.stderr:
                    logger.error("Error output:")
                    for line in result.stderr.strip().split('\n'):
                        logger.error(f"   {line}")
                
                # Send failure notification
                if ENABLE_EMAIL_NOTIFICATIONS:
                    self.send_notification(
                        subject="❌ Crypto Events Scraper - Failed",
                        body=f"Scraper failed at {run_start}\n\nError: {result.stderr}"
                    )
        
        except subprocess.TimeoutExpired:
            self.total_runs += 1
            logger.error("⏰ Scraper timed out after 1 hour")
            if ENABLE_EMAIL_NOTIFICATIONS:
                self.send_notification(
                    subject="⏰ Crypto Events Scraper - Timeout",
                    body=f"Scraper timed out at {run_start}"
                )
        
        except Exception as e:
            self.total_runs += 1
            logger.exception(f"💥 Unexpected error running scraper: {e}")
            if ENABLE_EMAIL_NOTIFICATIONS:
                self.send_notification(
                    subject="💥 Crypto Events Scraper - Error",
                    body=f"Unexpected error at {run_start}: {str(e)}"
                )
        
        run_end = datetime.now()
        runtime = (run_end - run_start).total_seconds()
        logger.info(f"⏱️  Run completed in {runtime:.1f} seconds")
        logger.info("=" * 60)

    def parse_scraper_output(self, output: str):
        """Parse scraper output to extract statistics."""
        stats = {}
        try:
            lines = output.split('\n')
            for line in lines:
                if 'New API events:' in line:
                    stats['api_events'] = int(line.split(':')[-1].strip())
                elif 'New web events:' in line:
                    stats['web_events'] = int(line.split(':')[-1].strip())
                elif 'Total new events:' in line:
                    stats['total_new'] = int(line.split(':')[-1].strip())
                elif 'Duplicates prevented:' in line:
                    stats['duplicates_prevented'] = int(line.split(':')[-1].strip())
                elif 'Runtime:' in line and 'seconds' in line:
                    stats['runtime'] = float(line.split(':')[-1].replace('seconds', '').strip())
            
            self.last_run_stats = stats
            
        except Exception as e:
            logger.debug(f"Failed to parse scraper output: {e}")

    def send_notification(self, subject: str, body: str):
        """Send email notification (if configured)."""
        try:
            msg = MimeMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            
            text = msg.as_string()
            server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
            server.quit()
            
            logger.info(f"📧 Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    def get_next_run_time(self):
        """Get the next scheduled run time."""
        jobs = schedule.get_jobs()
        if jobs:
            return jobs[0].next_run
        return None

    def status_report(self):
        """Print current scheduler status."""
        next_run = self.get_next_run_time()
        
        logger.info("📊 SCHEDULER STATUS REPORT")
        logger.info("=" * 40)
        logger.info(f"🕐 Scheduled time: {SCHEDULE_TIME} daily")
        logger.info(f"⏰ Next run: {next_run}")
        logger.info(f"📈 Total runs: {self.total_runs}")
        logger.info(f"✅ Successful: {self.successful_runs}")
        logger.info(f"❌ Failed: {self.total_runs - self.successful_runs}")
        
        if self.total_runs > 0:
            success_rate = (self.successful_runs / self.total_runs) * 100
            logger.info(f"📊 Success rate: {success_rate:.1f}%")
        
        if self.last_run_stats:
            logger.info(f"📋 Last run stats: {self.last_run_stats}")
        
        logger.info(f"📁 Scraper script: {SCRAPER_SCRIPT}")
        logger.info(f"📝 Log file: {LOG_FILE}")
        logger.info("=" * 40)

def main():
    """Main scheduler function."""
    logger.info("🚀 Crypto Events Scraper Scheduler Starting")
    logger.info(f"⏰ Configured to run daily at {SCHEDULE_TIME}")
    
    # Verify scraper script exists
    if not os.path.exists(SCRAPER_SCRIPT):
        logger.error(f"❌ Scraper script not found: {SCRAPER_SCRIPT}")
        logger.error("Please ensure automated_hybrid_scraper.py is in the same directory")
        return
    
    # Initialize scheduler
    scheduler = ScraperScheduler()
    
    # Schedule daily job
    schedule.every().day.at(SCHEDULE_TIME).do(scheduler.run_scraper)
    
    logger.info(f"✅ Scheduled daily execution at {SCHEDULE_TIME}")
    logger.info("📊 Starting scheduler status reports...")
    
    # Print status every hour
    def hourly_status():
        scheduler.status_report()
    
    schedule.every().hour.do(hourly_status)
    
    # Initial status report
    scheduler.status_report()
    
    # Optional: Run immediately for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        logger.info("🧪 Running scraper immediately for testing...")
        scheduler.run_scraper()
    
    # Main scheduler loop
    try:
        logger.info("🔄 Scheduler running... (Press Ctrl+C to stop)")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped by user")
    except Exception as e:
        logger.exception(f"💥 Scheduler error: {e}")

if __name__ == "__main__":
    main()