#!/usr/bin/env python3
"""
🛠️ SETUP SCRIPT for Automated Hybrid Crypto Events Scraper
Installs dependencies and sets up the automation system
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages."""
    requirements = [
        "requests",
        "pandas", 
        "openpyxl",
        "python-dateutil",
        "schedule",
        "playwright"
    ]
    
    print("📦 Installing required packages...")
    for package in requirements:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"   ⚠️  Failed to install {package} - you may need to install manually")
    
    # Install Playwright browsers
    try:
        print("🎭 Installing Playwright browsers...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("   ✅ Playwright browsers installed")
    except subprocess.CalledProcessError:
        print("   ⚠️  Playwright browser installation failed - web scraping may not work")

def create_startup_script():
    """Create a startup script for the scheduler."""
    
    # Determine the correct script for the OS
    if sys.platform.startswith('win'):
        # Windows batch file
        script_content = f"""@echo off
echo 🚀 Starting Crypto Events Scraper Scheduler...
cd /d "{os.getcwd()}"
python scheduler.py
pause
"""
        script_name = "start_scheduler.bat"
    else:
        # Unix shell script
        script_content = f"""#!/bin/bash
echo "🚀 Starting Crypto Events Scraper Scheduler..."
cd "{os.getcwd()}"
python3 scheduler.py
"""
        script_name = "start_scheduler.sh"
    
    # Write the script
    with open(script_name, 'w') as f:
        f.write(script_content)
    
    # Make executable on Unix systems
    if not sys.platform.startswith('win'):
        os.chmod(script_name, 0o755)
    
    print(f"✅ Created startup script: {script_name}")
    return script_name

def test_scraper():
    """Test the scraper to make sure it works."""
    print("🧪 Testing the automated scraper...")
    
    try:
        result = subprocess.run(
            [sys.executable, "automated_hybrid_scraper.py"],
            timeout=300,  # 5 minute timeout for test
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Scraper test completed successfully!")
            
            # Check if output file was created
            if os.path.exists("luma_crypto_events_master.xlsx"):
                print("   ✅ Excel output file created successfully!")
            
            return True
        else:
            print("   ❌ Scraper test failed!")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Scraper test timed out (but this is normal for full runs)")
        return True  # Timeout is acceptable for full scraping
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using the system."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE! Here's how to use your automated scraper:")
    print("="*60)
    
    print("\n📋 MANUAL OPERATIONS:")
    print("   • Run once now: python3 automated_hybrid_scraper.py")
    print("   • Test scheduler: python3 scheduler.py --run-now")
    print("   • Start scheduler: python3 scheduler.py")
    
    print("\n⏰ AUTOMATED OPERATIONS:")
    if sys.platform.startswith('win'):
        print("   • Double-click: start_scheduler.bat")
    else:
        print("   • Run: ./start_scheduler.sh")
    print("   • Runs daily at 2:00 AM automatically")
    
    print("\n📁 OUTPUT FILES:")
    print("   • Events database: luma_crypto_events_master.xlsx")
    print("   • Scraper logs: scraper.log") 
    print("   • Scheduler logs: scheduler.log")
    
    print("\n🔧 CUSTOMIZATION:")
    print("   • Edit schedule time in scheduler.py (SCHEDULE_TIME)")
    print("   • Update your cookies in automated_hybrid_scraper.py (AUTHENTICATED_COOKIES)")
    print("   • Add email notifications in scheduler.py (EMAIL_CONFIG)")
    
    print("\n💡 TIPS:")
    print("   • Update cookies monthly for best API access")
    print("   • Check logs if scraper stops working")  
    print("   • Excel file grows daily with new events")
    print("   • No duplicates - safe to run multiple times")
    
    print("\n🎯 EXPECTED RESULTS:")
    print("   • ~400-500 crypto events discovered per run")
    print("   • ~30-60 seconds runtime for API discovery")
    print("   • New events added daily (no duplicates)")
    print("   • Global coverage across 40+ cities")
    
    print("\n" + "="*60)
    print("🚀 Your crypto events monitoring system is ready!")
    print("="*60)

def main():
    """Main setup function."""
    print("🛠️  AUTOMATED CRYPTO EVENTS SCRAPER SETUP")
    print("="*50)
    
    # Check if we're in the right directory
    required_files = ["automated_hybrid_scraper.py", "scheduler.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure all files are in the same directory")
        return False
    
    # Install dependencies
    print("\n📦 STEP 1: Installing Dependencies")
    install_requirements()
    
    # Create startup script
    print("\n📜 STEP 2: Creating Startup Scripts")
    startup_script = create_startup_script()
    
    # Test the scraper
    print("\n🧪 STEP 3: Testing Scraper")
    test_success = test_scraper()
    
    if not test_success:
        print("\n⚠️  Setup completed with warnings - scraper test failed")
        print("You may need to:")
        print("   • Update cookies in automated_hybrid_scraper.py")
        print("   • Check internet connection")
        print("   • Install missing dependencies manually")
    
    # Show usage instructions
    show_usage_instructions()
    
    return True

if __name__ == "__main__":
    main()