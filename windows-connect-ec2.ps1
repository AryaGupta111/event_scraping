# Windows PowerShell Script to Connect to EC2
# Save this file and run it to easily connect to your EC2 instance

# Configuration - UPDATE THESE VALUES
$EC2_IP = "YOUR_PUBLIC_IP"  # Replace with your EC2 public IP
$KEY_PATH = "$env:USERPROFILE\Downloads\crypto-events-key.pem"  # Path to your .pem key

# Colors
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚀 Crypto Events - EC2 Connection Script            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if key file exists
if (-Not (Test-Path $KEY_PATH)) {
    Write-Host "❌ Error: Key file not found at $KEY_PATH" -ForegroundColor $RED
    Write-Host ""
    Write-Host "Please update the KEY_PATH variable in this script" -ForegroundColor $YELLOW
    Write-Host "Current path: $KEY_PATH" -ForegroundColor $YELLOW
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Key file found" -ForegroundColor $GREEN
Write-Host ""

# Check if EC2_IP is set
if ($EC2_IP -eq "YOUR_PUBLIC_IP") {
    Write-Host "❌ Error: Please update EC2_IP in this script" -ForegroundColor $RED
    Write-Host ""
    Write-Host "Edit this file and replace YOUR_PUBLIC_IP with your actual EC2 IP" -ForegroundColor $YELLOW
    Write-Host ""
    pause
    exit 1
}

# Set key permissions (Windows)
Write-Host "🔧 Setting key file permissions..." -ForegroundColor $YELLOW
try {
    icacls.exe $KEY_PATH /reset | Out-Null
    icacls.exe $KEY_PATH /grant:r "$($env:USERNAME):(R)" | Out-Null
    icacls.exe $KEY_PATH /inheritance:r | Out-Null
    Write-Host "✅ Key permissions set" -ForegroundColor $GREEN
} catch {
    Write-Host "⚠️  Warning: Could not set key permissions" -ForegroundColor $YELLOW
}

Write-Host ""
Write-Host "🌐 Connecting to EC2 instance..." -ForegroundColor $YELLOW
Write-Host "   IP: $EC2_IP" -ForegroundColor Cyan
Write-Host "   User: ubuntu" -ForegroundColor Cyan
Write-Host ""

# Connect via SSH
ssh -i $KEY_PATH ubuntu@$EC2_IP

# If connection fails
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Connection failed!" -ForegroundColor $RED
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor $YELLOW
    Write-Host "1. Check EC2 Security Group allows SSH (port 22)" -ForegroundColor $YELLOW
    Write-Host "2. Verify EC2 instance is running" -ForegroundColor $YELLOW
    Write-Host "3. Check EC2_IP is correct: $EC2_IP" -ForegroundColor $YELLOW
    Write-Host "4. Ensure OpenSSH Client is installed (Windows Settings)" -ForegroundColor $YELLOW
    Write-Host ""
}

pause
