# Windows PowerShell Script to Upload Files to EC2
# Save this file and run it to upload your project files

# Configuration - UPDATE THESE VALUES
$EC2_IP = "YOUR_PUBLIC_IP"  # Replace with your EC2 public IP
$KEY_PATH = "$env:USERPROFILE\Downloads\crypto-events-key.pem"  # Path to your .pem key
$PROJECT_PATH = "D:\events_scrapper"  # Path to your project folder

# Colors
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     📦 Crypto Events - File Upload Script               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if key file exists
if (-Not (Test-Path $KEY_PATH)) {
    Write-Host "❌ Error: Key file not found at $KEY_PATH" -ForegroundColor $RED
    pause
    exit 1
}

# Check if project folder exists
if (-Not (Test-Path $PROJECT_PATH)) {
    Write-Host "❌ Error: Project folder not found at $PROJECT_PATH" -ForegroundColor $RED
    Write-Host ""
    Write-Host "Please update PROJECT_PATH in this script" -ForegroundColor $YELLOW
    pause
    exit 1
}

Write-Host "✅ Key file found" -ForegroundColor $GREEN
Write-Host "✅ Project folder found" -ForegroundColor $GREEN
Write-Host ""

# Check if EC2_IP is set
if ($EC2_IP -eq "YOUR_PUBLIC_IP") {
    Write-Host "❌ Error: Please update EC2_IP in this script" -ForegroundColor $RED
    pause
    exit 1
}

Write-Host "📦 Creating zip file..." -ForegroundColor $YELLOW
$ZIP_PATH = "$env:TEMP\crypto-events.zip"

try {
    # Remove old zip if exists
    if (Test-Path $ZIP_PATH) {
        Remove-Item $ZIP_PATH -Force
    }

    # Create zip file
    Compress-Archive -Path "$PROJECT_PATH\*" -DestinationPath $ZIP_PATH -Force
    Write-Host "✅ Zip file created: $ZIP_PATH" -ForegroundColor $GREEN
} catch {
    Write-Host "❌ Error creating zip file: $_" -ForegroundColor $RED
    pause
    exit 1
}

Write-Host ""
Write-Host "📤 Uploading to EC2..." -ForegroundColor $YELLOW
Write-Host "   From: $ZIP_PATH" -ForegroundColor Cyan
Write-Host "   To: ubuntu@$EC2_IP:~/" -ForegroundColor Cyan
Write-Host ""

# Upload via SCP
scp -i $KEY_PATH $ZIP_PATH ubuntu@${EC2_IP}:~/crypto-events.zip

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Upload successful!" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor $YELLOW
    Write-Host "1. Connect to EC2: ssh -i $KEY_PATH ubuntu@$EC2_IP" -ForegroundColor Cyan
    Write-Host "2. Unzip files: unzip crypto-events.zip -d crypto-events" -ForegroundColor Cyan
    Write-Host "3. Follow deployment guide" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Upload failed!" -ForegroundColor $RED
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor $YELLOW
    Write-Host "1. Check EC2 Security Group allows SSH (port 22)" -ForegroundColor $YELLOW
    Write-Host "2. Verify EC2 instance is running" -ForegroundColor $YELLOW
    Write-Host "3. Check EC2_IP is correct: $EC2_IP" -ForegroundColor $YELLOW
    Write-Host ""
}

# Cleanup
Remove-Item $ZIP_PATH -Force

pause
