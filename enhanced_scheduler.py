#!/usr/bin/env python3
"""
⏰ ENHANCED SCHEDULER for Complete Crypto Events Pipeline
Scrapes events + automatically publishes to WordPress + manages everything
"""

import schedule
import time
import subprocess
import logging
import smtplib
import os
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sys

# ============= CONFIGURATION =============

# Choose your pipeline mode
PIPELINE_MODES = {
    "scraper_only": "automated_hybrid_scraper.py",          # Excel only
    "wordpress_pipeline": "integrated_scraper_wordpress.py", # Excel + WordPress
    "wordpress_only": "wordpress_importer.py"               # WordPress from existing Excel
}

# Select your preferred mode
PIPELINE_MODE = "wordpress_pipeline"  # Change this to your preferred mode
SCRAPER_SCRIPT = PIPELINE_MODES[PIPELINE_MODE]

# Schedule configuration
SCHEDULE_TIME = "02:00"  # 2:00 AM daily
ENABLE_STATUS_REPORTS = True  # Hourly status reports
LOG_FILE = "enhanced_scheduler.log"

# Email notifications (configure if desired)
ENABLE_EMAIL_NOTIFICATIONS = False
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "your_email@gmail.com"
}

# Monitoring configuration
ENABLE_WEBSITE_CHECK = False  # Check if events appear on website
WEBSITE_CHECK_URL = "https://yoursite.com/events"  # Your events page URL

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("enhanced-scheduler")

class EnhancedScraperScheduler:
    def __init__(self):
        self.total_runs = 0
        self.successful_runs = 0
        self.last_run_stats = {}
        self.pipeline_history = []
        
    def run_pipeline(self):
        """Execute the complete crypto events pipeline."""
        run_start = datetime.now()
        run_id = f"run_{self.total_runs + 1}_{run_start.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info("🚀 STARTING CRYPTO EVENTS PIPELINE")
        logger.info("=" * 60)
        logger.info(f"🆔 Run ID: {run_id}")
        logger.info(f"📋 Pipeline: {PIPELINE_MODE}")
        logger.info(f"📜 Script: {SCRAPER_SCRIPT}")
        logger.info(f"⏰ Started: {run_start}")
        
        try:
            # Execute the pipeline script
            result = subprocess.run(
                [sys.executable, SCRAPER_SCRIPT],
                capture_output=True,
                text=True,
                timeout=7200  # 2 hour timeout
            )
            
            run_end = datetime.now()
            runtime = (run_end - run_start).total_seconds()
            
            if result.returncode == 0:
                # Success
                self.successful_runs += 1
                self.total_runs += 1
                
                logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
                logger.info(f"⏱️  Runtime: {runtime:.1f} seconds")
                logger.info(f"📊 Success rate: {self.successful_runs}/{self.total_runs} ({(self.successful_runs/self.total_runs)*100:.1f}%)")
                
                # Parse and log output
                stats = self.parse_pipeline_output(result.stdout)
                self.last_run_stats = stats
                
                # Log key metrics
                if stats:
                    if 'events_found' in stats:
                        logger.info(f"📋 Events discovered: {stats['events_found']}")
                    if 'events_imported' in stats:
                        logger.info(f"🌐 Events published to WordPress: {stats['events_imported']}")
                    if 'events_updated' in stats:
                        logger.info(f"🔄 Events updated on WordPress: {stats['events_updated']}")
                
                # Store run history
                self.pipeline_history.append({
                    "run_id": run_id,
                    "start_time": run_start,
                    "end_time": run_end,
                    "runtime": runtime,
                    "success": True,
                    "stats": stats
                })
                
                # Website verification (if enabled)
                if ENABLE_WEBSITE_CHECK:
                    self.verify_website_events()
                
                # Send success notification
                if ENABLE_EMAIL_NOTIFICATIONS:
                    self.send_notification(
                        subject="✅ Crypto Events Pipeline - Success",
                        body=self.build_success_email_body(run_start, runtime, stats)
                    )
                    
            else:
                # Failure
                self.total_runs += 1
                logger.error("❌ PIPELINE FAILED!")
                logger.error(f"⏱️  Runtime: {runtime:.1f} seconds")
                logger.error(f"🔢 Return code: {result.returncode}")
                
                if result.stderr:
                    logger.error("Error output:")
                    for line in result.stderr.strip().split('\n'):
                        logger.error(f"   {line}")
                
                # Store failed run
                self.pipeline_history.append({
                    "run_id": run_id,
                    "start_time": run_start,
                    "end_time": run_end,
                    "runtime": runtime,
                    "success": False,
                    "error": result.stderr
                })
                
                # Send failure notification
                if ENABLE_EMAIL_NOTIFICATIONS:
                    self.send_notification(
                        subject="❌ Crypto Events Pipeline - Failed",
                        body=f"Pipeline failed at {run_start}\n\nError: {result.stderr}"
                    )
        
        except subprocess.TimeoutExpired:
            self.total_runs += 1
            runtime = (datetime.now() - run_start).total_seconds()
            logger.error("⏰ PIPELINE TIMED OUT (2 hours)")
            logger.error(f"⏱️  Runtime before timeout: {runtime:.1f} seconds")
            
            if ENABLE_EMAIL_NOTIFICATIONS:
                self.send_notification(
                    subject="⏰ Crypto Events Pipeline - Timeout",
                    body=f"Pipeline timed out after 2 hours at {run_start}"
                )
        
        except Exception as e:
            self.total_runs += 1
            runtime = (datetime.now() - run_start).total_seconds()
            logger.exception(f"💥 UNEXPECTED PIPELINE ERROR: {e}")
            logger.error(f"⏱️  Runtime before error: {runtime:.1f} seconds")
            
            if ENABLE_EMAIL_NOTIFICATIONS:
                self.send_notification(
                    subject="💥 Crypto Events Pipeline - Error",
                    body=f"Unexpected error at {run_start}: {str(e)}"
                )
        
        logger.info("=" * 60)

    def parse_pipeline_output(self, output: str) -> dict:
        """Parse pipeline output to extract key statistics."""
        stats = {}
        try:
            lines = output.split('\n')
            for line in lines:
                # Scraper stats
                if 'Total new events:' in line:
                    stats['events_found'] = int(line.split(':')[-1].strip())
                elif 'API events found:' in line:
                    stats['api_events'] = int(line.split(':')[-1].strip())
                elif 'Web events found:' in line:
                    stats['web_events'] = int(line.split(':')[-1].strip())
                
                # WordPress stats
                elif 'Events imported:' in line:
                    stats['events_imported'] = int(line.split(':')[-1].strip())
                elif 'Events updated:' in line:
                    stats['events_updated'] = int(line.split(':')[-1].strip())
                elif 'Events skipped:' in line:
                    stats['events_skipped'] = int(line.split(':')[-1].strip())
                
                # Runtime stats
                elif 'Runtime:' in line and 'seconds' in line:
                    stats['runtime'] = float(line.split(':')[-1].replace('seconds', '').strip())
            
            return stats
            
        except Exception as e:
            logger.debug(f"Failed to parse pipeline output: {e}")
            return {}

    def verify_website_events(self):
        """Verify that events appear on the website."""
        try:
            import requests
            logger.info("🌐 Verifying events on website...")
            
            response = requests.get(WEBSITE_CHECK_URL, timeout=30)
            if response.status_code == 200:
                # Simple check for event-related content
                content = response.text.lower()
                event_indicators = ['crypto', 'blockchain', 'web3', 'event', 'conference']
                
                found_indicators = sum(1 for indicator in event_indicators if indicator in content)
                
                if found_indicators >= 3:
                    logger.info("   ✅ Website verification successful - events appear to be present")
                else:
                    logger.warning("   ⚠️  Website verification inconclusive - limited event content detected")
            else:
                logger.warning(f"   ⚠️  Website check failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.warning(f"   ⚠️  Website verification failed: {e}")

    def build_success_email_body(self, start_time, runtime, stats):
        """Build detailed success email body."""
        body = f"""🎉 Crypto Events Pipeline Completed Successfully!

⏰ Execution Details:
• Started: {start_time}
• Runtime: {runtime:.1f} seconds
• Pipeline: {PIPELINE_MODE}

📊 Results Summary:"""
        
        if stats:
            if 'events_found' in stats:
                body += f"\n• 🔍 Events discovered: {stats['events_found']}"
            if 'api_events' in stats:
                body += f"\n• ⚡ API events: {stats['api_events']}"
            if 'web_events' in stats:
                body += f"\n• 🌐 Web scraped events: {stats['web_events']}"
            if 'events_imported' in stats:
                body += f"\n• 📝 WordPress imports: {stats['events_imported']}"
            if 'events_updated' in stats:
                body += f"\n• 🔄 WordPress updates: {stats['events_updated']}"
        
        body += f"""

📈 Overall Statistics:
• Total runs: {self.total_runs}
• Successful runs: {self.successful_runs}
• Success rate: {(self.successful_runs/self.total_runs)*100:.1f}%

🌐 Your crypto events are live at: {WEBSITE_CHECK_URL}

This is an automated message from your Crypto Events Pipeline."""
        
        return body

    def send_notification(self, subject: str, body: str):
        """Send email notification."""
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
        """Comprehensive status report."""
        next_run = self.get_next_run_time()
        
        logger.info("📊 CRYPTO EVENTS PIPELINE STATUS")
        logger.info("=" * 50)
        logger.info(f"🕐 Schedule: {SCHEDULE_TIME} daily")
        logger.info(f"⏰ Next run: {next_run}")
        logger.info(f"📋 Pipeline mode: {PIPELINE_MODE}")
        logger.info(f"📜 Script: {SCRAPER_SCRIPT}")
        logger.info(f"📈 Total runs: {self.total_runs}")
        logger.info(f"✅ Successful: {self.successful_runs}")
        logger.info(f"❌ Failed: {self.total_runs - self.successful_runs}")
        
        if self.total_runs > 0:
            success_rate = (self.successful_runs / self.total_runs) * 100
            logger.info(f"📊 Success rate: {success_rate:.1f}%")
        
        if self.last_run_stats:
            logger.info(f"📋 Last run results:")
            for key, value in self.last_run_stats.items():
                logger.info(f"   • {key}: {value}")
        
        # Recent history
        if self.pipeline_history:
            recent_runs = self.pipeline_history[-3:]  # Last 3 runs
            logger.info(f"📈 Recent runs:")
            for run in recent_runs:
                status = "✅" if run['success'] else "❌"
                logger.info(f"   {status} {run['start_time'].strftime('%Y-%m-%d %H:%M')} - {run['runtime']:.1f}s")
        
        logger.info(f"📁 Log file: {LOG_FILE}")
        logger.info("=" * 50)

def main():
    """Main scheduler function."""
    logger.info("🚀 ENHANCED CRYPTO EVENTS SCHEDULER STARTING")
    logger.info(f"⚙️  Pipeline mode: {PIPELINE_MODE}")
    logger.info(f"⏰ Schedule: Daily at {SCHEDULE_TIME}")
    
    # Verify pipeline script exists
    if not os.path.exists(SCRAPER_SCRIPT):
        logger.error(f"❌ Pipeline script not found: {SCRAPER_SCRIPT}")
        logger.error("Available scripts:")
        for mode, script in PIPELINE_MODES.items():
            exists = "✅" if os.path.exists(script) else "❌"
            logger.error(f"   {exists} {mode}: {script}")
        return
    
    # Initialize scheduler
    scheduler = EnhancedScraperScheduler()
    
    # Schedule daily pipeline
    schedule.every().day.at(SCHEDULE_TIME).do(scheduler.run_pipeline)
    logger.info(f"✅ Scheduled daily execution at {SCHEDULE_TIME}")
    
    # Optional status reports
    if ENABLE_STATUS_REPORTS:
        schedule.every().hour.do(scheduler.status_report)
        logger.info("📊 Enabled hourly status reports")
    
    # Initial status report
    scheduler.status_report()
    
    # Optional: Run immediately for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        logger.info("🧪 Running pipeline immediately for testing...")
        scheduler.run_pipeline()
    
    # Main scheduler loop
    try:
        logger.info("🔄 Scheduler active... (Press Ctrl+C to stop)")
        logger.info("💡 Run with --run-now to test immediately")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped by user")
    except Exception as e:
        logger.exception(f"💥 Scheduler error: {e}")

if __name__ == "__main__":
    main()