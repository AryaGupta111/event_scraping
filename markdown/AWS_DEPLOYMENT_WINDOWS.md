# 🚀 AWS EC2 Deployment Guide - Windows Users

Complete guide to deploy your Crypto Events app on AWS EC2 from Windows.

---

## 📋 What You'll Deploy

- ✅ **EC2 Instance**: Ubuntu server (t2.micro - free tier eligible)
- ✅ **Flask API**: Running with Gunicorn
- ✅ **Nginx**: Reverse proxy + serve frontend
- ✅ **Systemd**: Auto-start services
- ✅ **Cron Job**: Daily scraping at midnight
- ✅ **SSL Certificate**: Free with Let's Encrypt (optional)

---

## 💰 Cost Estimate

### Free Tier (First 12 Months)
- **EC2 t2.micro**: 750 hours/month FREE
- **Storage**: 30 GB FREE
- **Data Transfer**: 15 GB/month FREE
- **MongoDB Atlas**: FREE (512 MB)
- **Total**: $0/month ✅

### After Free Tier
- **EC2 t2.micro**: ~$8-10/month
- **Storage (30 GB)**: ~$3/month
- **Total**: ~$11-13/month

---

## 🎯 Prerequisites

1. ✅ AWS Account (sign up at https://aws.amazon.com)
2. ✅ MongoDB Atlas connection string
3. ✅ Domain name (optional, for custom domain)
4. ✅ Windows 10/11 with PowerShell or Command Prompt
5. ✅ 30-45 minutes of time

---

## 📦 Part 1: Create EC2 Instance (10 minutes)

### Step 1.1: Launch EC2 Instance

1. **Login to AWS Console**: https://console.aws.amazon.com
2. **Go to EC2**: Services → EC2
3. **Click**: "Launch Instance"

### Step 1.2: Configure Instance

**Name and Tags:**
```
Name: crypto-events-server
```

**Application and OS Images (AMI):**
```
OS: Ubuntu Server 22.04 LTS (Free tier eligible)
Architecture: 64-bit (x86)
```

**Instance Type:**
```
Type: t2.micro (Free tier eligible)
vCPUs: 1
Memory: 1 GiB
```

**Key Pair (Login):**
```
1. Click "Create new key pair"
2. Name: crypto-events-key
3. Type: RSA
4. Format: .pem (we'll convert for Windows)
5. Download and save to: C:\Users\YourUsername\Downloads\
```

**Network Settings:**
```
✅ Allow SSH traffic from: My IP (or Anywhere for testing)
✅ Allow HTTPS traffic from the internet
✅ Allow HTTP traffic from the internet
```

**Configure Storage:**
```
Size: 30 GiB (Free tier eligible)
Type: gp3 (General Purpose SSD)
```

### Step 1.3: Launch

1. **Review** all settings
2. **Click**: "Launch Instance"
3. **Wait**: 2-3 minutes for instance to start
4. **Note**: Your instance's Public IP address (e.g., 54.123.45.67)

---

## 🔐 Part 2: Connect to Your Server from Windows (10 minutes)

### Option A: Using PowerShell (Windows 10/11 Built-in) ⭐ Recommended

#### Step 2A.1: Open PowerShell

1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"

#### Step 2A.2: Navigate to Key Location

```powershell
# Navigate to Downloads folder
cd $env:USERPROFILE\Downloads

# Check if key file exists
dir crypto-events-key.pem
```

#### Step 2A.3: Set Key Permissions (Important!)

```powershell
# Remove inheritance and set proper permissions
icacls.exe crypto-events-key.pem /reset
icacls.exe crypto-events-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe crypto-events-key.pem /inheritance:r
```

#### Step 2A.4: Connect via SSH

```powershell
# Replace YOUR_PUBLIC_IP with your EC2 instance's public IP
ssh -i crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP

# Example:
# ssh -i crypto-events-key.pem ubuntu@54.123.45.67

# If prompted "Are you sure you want to continue connecting?", type: yes
```

**If SSH command not found:**
```powershell
# Enable OpenSSH Client (Windows 10/11)
# Go to: Settings → Apps → Optional Features → Add a feature
# Search for "OpenSSH Client" and install
```

---

### Option B: Using PuTTY (Alternative Method)

#### Step 2B.1: Download PuTTY

1. **Download PuTTY**: https://www.putty.org/
2. **Download**: putty.exe and puttygen.exe
3. **Save to**: C:\Program Files\PuTTY\ (or any folder)

#### Step 2B.2: Convert .pem to .ppk

1. **Open PuTTYgen** (puttygen.exe)
2. **Click**: "Load"
3. **Change file type** to "All Files (*.*)"
4. **Select**: crypto-events-key.pem
5. **Click**: "Save private key"
6. **Click**: "Yes" (save without passphrase)
7. **Save as**: crypto-events-key.ppk

#### Step 2B.3: Connect with PuTTY

1. **Open PuTTY** (putty.exe)
2. **Host Name**: ubuntu@YOUR_PUBLIC_IP
   - Example: ubuntu@54.123.45.67
3. **Port**: 22
4. **Connection type**: SSH
5. **Left panel**: Connection → SSH → Auth → Credentials
6. **Private key file**: Browse to crypto-events-key.ppk
7. **Click**: "Open"
8. **If security alert**: Click "Accept"

---

### Option C: Using Windows Subsystem for Linux (WSL)

#### Step 2C.1: Install WSL (if not already installed)

```powershell
# Open PowerShell as Administrator
wsl --install

# Restart computer if prompted
```

#### Step 2C.2: Connect via WSL

```bash
# Open WSL (Ubuntu)
wsl

# Copy key to WSL
cp /mnt/c/Users/YourUsername/Downloads/crypto-events-key.pem ~/

# Set permissions
chmod 400 ~/crypto-events-key.pem

# Connect
ssh -i ~/crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
```

---

## 🛠️ Part 3: Setup Server (15 minutes)

**Note**: Once connected via SSH, all commands are the same regardless of your Windows connection method!

### Step 3.1: Update System

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y
```

### Step 3.2: Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx (web server)
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Install other dependencies
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### Step 3.3: Upload Your Project Files

**Option 1: Using Git (Recommended)**

```bash
# Clone your repository
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**Option 2: Upload Files from Windows**

**Using PowerShell (SCP):**

```powershell
# On your Windows machine, navigate to project folder
cd D:\events_scrapper

# Create a zip file first
Compress-Archive -Path * -DestinationPath crypto-events.zip

# Upload to EC2
scp -i $env:USERPROFILE\Downloads\crypto-events-key.pem crypto-events.zip ubuntu@YOUR_PUBLIC_IP:~/
```

**Then on EC2 server:**

```bash
# Install unzip
sudo apt install -y unzip

# Unzip files
unzip crypto-events.zip -d crypto-events
cd crypto-events
```

**Using WinSCP (GUI Method):**

1. **Download WinSCP**: https://winscp.net/
2. **Install and open WinSCP**
3. **New Session**:
   - File protocol: SFTP
   - Host name: YOUR_PUBLIC_IP
   - Port: 22
   - User name: ubuntu
4. **Advanced** → SSH → Authentication
   - Private key file: Browse to crypto-events-key.ppk
5. **Login**
6. **Drag and drop** your project files to /home/ubuntu/

### Step 3.4: Setup Project Directory

```bash
# Navigate to project
cd ~/crypto-events  # or ~/YOUR_REPO

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn
```

### Step 3.5: Configure Environment Variables

```bash
# Create .env file
nano .env

# Add these lines (replace with your MongoDB URI):
MONGODB_URI=mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0
PORT=5000
API_HOST=0.0.0.0
PYTHON_VERSION=3.12.0

# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 3.6: Test Your Application

```bash
# Test the scraper
python scraper_mongodb.py

# Test the API server
python api_server.py

# If it works, press Ctrl+C to stop
```

---

## 🔧 Part 4: Setup Systemd Services (10 minutes)

### Step 4.1: Create API Service

```bash
# Get your project path
PROJECT_PATH=$(pwd)
echo "Project path: $PROJECT_PATH"

# Create service file
sudo nano /etc/systemd/system/crypto-events-api.service
```

**Add this content (replace /home/ubuntu/crypto-events with your actual path):**

```ini
[Unit]
Description=Crypto Events API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/crypto-events
Environment="PATH=/home/ubuntu/crypto-events/venv/bin"
EnvironmentFile=/home/ubuntu/crypto-events/.env
ExecStart=/home/ubuntu/crypto-events/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save**: Ctrl+O, Enter, Ctrl+X

### Step 4.2: Setup Daily Scraper Cron Job

```bash
# Edit crontab
crontab -e

# Choose nano (option 1) if asked

# Add this line at the end (replace path with your actual path):
0 0 * * * /home/ubuntu/crypto-events/venv/bin/python /home/ubuntu/crypto-events/scraper_mongodb.py >> /home/ubuntu/scraper.log 2>&1

# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 4.3: Start and Enable Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start API service
sudo systemctl start crypto-events-api

# Enable API service (auto-start on boot)
sudo systemctl enable crypto-events-api

# Check status
sudo systemctl status crypto-events-api

# If you see "active (running)" - SUCCESS! ✅
# Press 'q' to exit status view
```

---

## 🌐 Part 5: Configure Nginx (10 minutes)

### Step 5.1: Get Your Public IP

```bash
# Get EC2 public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

### Step 5.2: Create Nginx Configuration

```bash
# Create config file
sudo nano /etc/nginx/sites-available/crypto-events
```

**Add this content (replace YOUR_PUBLIC_IP with your actual IP):**

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;  # Replace with your IP or domain

    # Serve frontend files
    location / {
        root /home/ubuntu/crypto-events;
        index events_api.html;
        try_files $uri $uri/ /events_api.html;
    }

    # Proxy API requests to Flask
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static files
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /home/ubuntu/crypto-events;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Save**: Ctrl+O, Enter, Ctrl+X

### Step 5.3: Enable Site and Restart Nginx

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/crypto-events /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test is successful, restart Nginx
sudo systemctl restart nginx

# Enable Nginx (auto-start on boot)
sudo systemctl enable nginx
```

---

## 🎨 Part 6: Update Frontend API URL (5 minutes)

### Step 6.1: Update JavaScript Files

```bash
# Edit events_api.js
nano ~/crypto-events/events_api.js
```

**Find this line:**
```javascript
const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') 
    ? 'http://localhost:5000/api' 
    : 'https://your-render-app.onrender.com/api';
```

**Replace with:**
```javascript
const API_BASE_URL = '/api';  // Since Nginx proxies /api to Flask
```

**Save**: Ctrl+O, Enter, Ctrl+X

### Step 6.2: Do the Same for list_event.js (if exists)

```bash
nano ~/crypto-events/list_event.js

# Update API_BASE_URL to '/api'
# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 6.3: Reload Nginx

```bash
sudo systemctl reload nginx
```

---

## ✅ Part 7: Test Your Deployment (5 minutes)

### Step 7.1: Test API Endpoints (from EC2)

```bash
# Test health endpoint
curl http://localhost/api/health

# Test events endpoint
curl http://localhost/api/events

# Test stats endpoint
curl http://localhost/api/stats
```

### Step 7.2: Test from Windows Browser

**Open your browser on Windows and visit:**

```
http://YOUR_PUBLIC_IP
```

**Example:**
```
http://54.123.45.67
```

You should see your crypto events website! 🎉

### Step 7.3: Test API from Windows PowerShell

```powershell
# Test from Windows
curl http://YOUR_PUBLIC_IP/api/health
curl http://YOUR_PUBLIC_IP/api/events
```

### Step 7.4: Test Cron Job (Manual Trigger)

```bash
# On EC2 server, run scraper manually to test
cd ~/crypto-events
source venv/bin/activate
python scraper_mongodb.py

# Check if events are being scraped
```

---

## 🔒 Part 8: Setup SSL Certificate (Optional - 15 minutes)

### Prerequisites
- You need a domain name (e.g., events.yourdomain.com)
- Domain should point to your EC2 public IP

### Step 8.1: Point Domain to EC2 (On Windows)

**On Hostinger (or your DNS provider):**

1. **Login to Hostinger**
2. **Go to**: Domains → DNS/Nameservers
3. **Add A Record**:
   ```
   Type: A Record
   Name: events (or @ for root domain)
   Points to: YOUR_EC2_PUBLIC_IP
   TTL: 3600
   ```
4. **Save**
5. **Wait**: 5-10 minutes for DNS propagation

**Test DNS from Windows PowerShell:**

```powershell
# Test if domain points to your EC2
nslookup events.yourdomain.com

# Should show your EC2 IP
```

### Step 8.2: Install Certbot (On EC2)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### Step 8.3: Get SSL Certificate

```bash
# Replace with your domain
sudo certbot --nginx -d events.yourdomain.com

# Follow the prompts:
# - Enter email address
# - Agree to terms (Y)
# - Share email? (N)
# - Redirect HTTP to HTTPS? (2 - Yes)
```

### Step 8.4: Test SSL from Windows

**Open browser:**
```
https://events.yourdomain.com
```

Should show secure connection! 🔒

### Step 8.5: Auto-Renewal

```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

---

## 📊 Part 9: Monitoring & Maintenance (from Windows)

### Connect to EC2 from Windows

**PowerShell:**
```powershell
# Save this command for easy access
ssh -i $env:USERPROFILE\Downloads\crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
```

**Create a shortcut (Optional):**

1. **Create file**: `connect-ec2.ps1`
2. **Add content**:
   ```powershell
   ssh -i $env:USERPROFILE\Downloads\crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
   ```
3. **Run**: Right-click → Run with PowerShell

### Check Service Status

```bash
# Check API service
sudo systemctl status crypto-events-api

# Check Nginx
sudo systemctl status nginx

# View API logs
sudo journalctl -u crypto-events-api -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View scraper logs
tail -f ~/scraper.log
```

### Restart Services

```bash
# Restart API
sudo systemctl restart crypto-events-api

# Restart Nginx
sudo systemctl restart nginx
```

### Update Your Application

**From Windows:**

```powershell
# Option 1: Push to GitHub, then pull on EC2
git add .
git commit -m "Update"
git push

# Then on EC2:
# ssh to server
# cd ~/crypto-events
# git pull
# sudo systemctl restart crypto-events-api
```

**Option 2: Upload files via WinSCP**

1. Open WinSCP
2. Connect to EC2
3. Upload changed files
4. Restart services

---

## 🔧 Part 10: Windows-Specific Tools & Tips

### Recommended Windows Tools

1. **Windows Terminal** (Modern terminal)
   - Download from Microsoft Store
   - Better than PowerShell/CMD

2. **WinSCP** (File transfer GUI)
   - https://winscp.net/
   - Easy drag-and-drop file transfer

3. **PuTTY** (SSH client)
   - https://www.putty.org/
   - Alternative to PowerShell SSH

4. **Visual Studio Code** (Code editor)
   - https://code.visualstudio.com/
   - Has Remote-SSH extension

### VS Code Remote SSH (Advanced)

1. **Install VS Code**
2. **Install Extension**: Remote - SSH
3. **Connect**:
   - Press F1
   - Type: "Remote-SSH: Connect to Host"
   - Enter: ubuntu@YOUR_PUBLIC_IP
   - Select key file
4. **Edit files** directly on EC2!

### Create Desktop Shortcuts

**SSH Connection Shortcut:**

1. **Create file**: `EC2-Connect.bat`
2. **Add content**:
   ```batch
   @echo off
   cd %USERPROFILE%\Downloads
   ssh -i crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
   pause
   ```
3. **Save** and double-click to connect

**Open Website Shortcut:**

1. **Create file**: `Open-Website.url`
2. **Add content**:
   ```
   [InternetShortcut]
   URL=http://YOUR_PUBLIC_IP
   ```
3. **Save** and double-click to open

---

## 🐛 Troubleshooting (Windows-Specific)

### SSH Connection Issues

**Problem**: "ssh: command not found"

**Solution**:
```powershell
# Enable OpenSSH Client
# Settings → Apps → Optional Features → Add a feature
# Search "OpenSSH Client" → Install
```

**Problem**: "Permission denied (publickey)"

**Solution**:
```powershell
# Fix key permissions
cd $env:USERPROFILE\Downloads
icacls.exe crypto-events-key.pem /reset
icacls.exe crypto-events-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe crypto-events-key.pem /inheritance:r
```

**Problem**: "Connection timed out"

**Solution**:
- Check EC2 Security Group allows SSH (port 22)
- Check your IP is allowed
- Try from different network

### File Upload Issues

**Problem**: Can't upload files via SCP

**Solution**: Use WinSCP (GUI) instead:
1. Download WinSCP
2. Use SFTP protocol
3. Drag and drop files

### PowerShell Issues

**Problem**: Scripts won't run

**Solution**:
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Quick Reference Commands (Windows)

### Connect to EC2

```powershell
# PowerShell
ssh -i $env:USERPROFILE\Downloads\crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
```

### Upload Files

```powershell
# PowerShell (SCP)
scp -i $env:USERPROFILE\Downloads\crypto-events-key.pem -r D:\events_scrapper\* ubuntu@YOUR_PUBLIC_IP:~/crypto-events/
```

### Test Website

```powershell
# PowerShell
curl http://YOUR_PUBLIC_IP/api/health
```

### Open in Browser

```powershell
# PowerShell
Start-Process "http://YOUR_PUBLIC_IP"
```

---

## ✅ Deployment Checklist

- [ ] AWS account created
- [ ] EC2 instance launched (t2.micro)
- [ ] Key pair downloaded (.pem file)
- [ ] Security group configured (SSH, HTTP, HTTPS)
- [ ] Connected via SSH from Windows
- [ ] System updated on EC2
- [ ] Dependencies installed
- [ ] Project files uploaded
- [ ] Virtual environment created
- [ ] Environment variables configured
- [ ] API service running
- [ ] Nginx configured
- [ ] Cron job scheduled
- [ ] Website accessible from Windows browser
- [ ] API endpoints responding
- [ ] Custom domain configured (optional)
- [ ] SSL certificate installed (optional)

---

## 🎉 Success!

Your crypto events app is now running on AWS EC2, deployed from Windows!

**Access your app from Windows:**
- HTTP: `http://YOUR_PUBLIC_IP`
- HTTPS: `https://events.yourdomain.com` (if SSL configured)

**API Endpoints:**
- Health: `http://YOUR_PUBLIC_IP/api/health`
- Events: `http://YOUR_PUBLIC_IP/api/events`
- Stats: `http://YOUR_PUBLIC_IP/api/stats`

---

## 📞 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com
- **Ubuntu Server Guide**: https://ubuntu.com/server/docs
- **Nginx Documentation**: https://nginx.org/en/docs
- **Windows SSH Guide**: https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse

---

## 🚀 Next Steps

1. ✅ Monitor logs for first 24 hours
2. ✅ Test cron job runs at midnight
3. ✅ Setup CloudWatch for monitoring (optional)
4. ✅ Configure automatic backups
5. ✅ Add custom domain with SSL
6. ✅ Create Windows shortcuts for easy access
7. ✅ Share your app with the world! 🌍

---

**Total Setup Time**: 45-60 minutes

**Monthly Cost**: $0 (free tier) or ~$11-13 after

**Result**: Full-stack crypto events platform on AWS, deployed from Windows! 🎉
