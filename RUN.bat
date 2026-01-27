@echo off
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║         🚀 Crypto Events System - One Click Setup       ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo This will:
echo   1. Check and install dependencies
echo   2. Connect to MongoDB Atlas
echo   3. Scrape events (if needed)
echo   4. Start the API server
echo.
echo ⚠️  IMPORTANT: Keep this window open after server starts!
echo.
echo After the server starts, open events_api.html in your browser
echo.
pause

python setup_and_run.py

echo.
echo Server stopped.
pause
