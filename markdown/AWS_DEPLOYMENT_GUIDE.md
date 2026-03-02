# 🚀 AWS EC2 Deployment Guide - Single Instance

Complete guide to deploy your Crypto Events app on AWS EC2 (single server).

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
4. ✅ 30-45 minutes of time

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
4. Format: .pem (for Mac/Linux) or .ppk (for Windows/PuTTY)
5. Download and save securely!
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
4. **Note**: Your instance's Public IP address

---

## 🔐 Part 2: Connect to Your Server (5 minutes)

### Step 2.1: Set Key Permissions (Mac/Linux)

```bash
# Navigate to where you saved the key
cd ~/Downloads

# Set correct permissions
chmod 400 crypto-events-key.pem
```

### Step 2.2: Connect via SSH

```bash
# Replace YOUR_PUBLIC_IP with your EC2 instance's public IP
ssh -i crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP

# Example:
# ssh -i crypto-events-key.pem ubuntu@54.123.45.67
```

### Step 2.3: For Windows Users (PuTTY)

1. **Download PuTTY**: https://www.putty.org
2. **Convert .pem to .ppk** using PuTTYgen
3. **Connect**:
   - Host: ubuntu@YOUR_PUBLIC_IP
   - Port: 22
   - Auth: Browse to your .ppk file

---

## 🛠️ Part 3: Setup Server (15 minutes)

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

### Step 3.3: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Or if you don't have it on GitHub yet, upload files manually
# We'll cover this in Step 3.4
```

### Step 3.4: Alternative - Upload Files Manually

If you don't have GitHub:

```bash
# On your local machine, create a zip file
# Then upload using SCP:

# Mac/Linux:
scp -i crypto-events-key.pem crypto-events.zip ubuntu@YOUR_PUBLIC_IP:~/

# On server, unzip:
sudo apt install -y unzip
unzip crypto-events.zip
```

### Step 3.5: Setup Project Directory

```bash
# Navigate to project
cd ~/YOUR_REPO  # or ~/crypto-events

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

### Step 3.6: Configure Environment Variables

```bash
# Create .env file
nano .env

# Add these lines (replace with your MongoDB URI):
MONGODB_URI=mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0
PORT=5000
API_HOST=0.0.0.0
PYTHON_VERSION=3.11.0

# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 3.7: Test Your Application

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
# Create service file
sudo nano /etc/systemd/system/crypto-events-api.service
```

**Add this content:**

```ini
[Unit]
Description=Crypto Events API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/YOUR_REPO
Environment="PATH=/home/ubuntu/YOUR_REPO/venv/bin"
EnvironmentFile=/home/ubuntu/YOUR_REPO/.env
ExecStart=/home/ubuntu/YOUR_REPO/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 api_server:app
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

# Add this line at the end (runs daily at midnight):
0 0 * * * /home/ubuntu/YOUR_REPO/venv/bin/python /home/ubuntu/YOUR_REPO/scraper_mongodb.py >> /home/ubuntu/scraper.log 2>&1

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
```

---

## 🌐 Part 5: Configure Nginx (10 minutes)

### Step 5.1: Create Nginx Configuration

```bash
# Create config file
sudo nano /etc/nginx/sites-available/crypto-events
```

**Add this content:**

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;  # Replace with your IP or domain

    # Serve frontend files
    location / {
        root /home/ubuntu/YOUR_REPO;
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
        root /home/ubuntu/YOUR_REPO;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Save**: Ctrl+O, Enter, Ctrl+X

### Step 5.2: Enable Site and Restart Nginx

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
nano ~/YOUR_REPO/events_api.js
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
nano ~/YOUR_REPO/list_event.js

# Update API_BASE_URL to '/api'
# Save: Ctrl+O, Enter, Ctrl+X
```

---

## ✅ Part 7: Test Your Deployment (5 minutes)

### Step 7.1: Test API Endpoints

```bash
# Test health endpoint
curl http://localhost/api/health

# Test events endpoint
curl http://localhost/api/events

# Test stats endpoint
curl http://localhost/api/stats
```

### Step 7.2: Test from Browser

Open your browser and visit:

```
http://YOUR_PUBLIC_IP
```

You should see your crypto events website! 🎉

### Step 7.3: Test Cron Job (Manual Trigger)

```bash
# Run scraper manually to test
cd ~/YOUR_REPO
source venv/bin/activate
python scraper_mongodb.py

# Check if events are being scraped
```

---

## 🔒 Part 8: Setup SSL Certificate (Optional - 15 minutes)

### Prerequisites
- You need a domain name (e.g., events.yourdomain.com)
- Domain should point to your EC2 public IP

### Step 8.1: Point Domain to EC2

**On Hostinger (or your DNS provider):**

```
Type: A Record
Name: events (or @ for root domain)
Points to: YOUR_EC2_PUBLIC_IP
TTL: 3600
```

Wait 5-10 minutes for DNS propagation.

### Step 8.2: Install Certbot

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
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)
```

### Step 8.4: Auto-Renewal

```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

### Step 8.5: Update Nginx Config

Certbot automatically updates your Nginx config. Verify:

```bash
sudo nano /etc/nginx/sites-available/crypto-events

# You should see SSL configuration added by Certbot
```

---

## 📊 Part 9: Monitoring & Maintenance

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

```bash
# Pull latest changes from GitHub
cd ~/YOUR_REPO
git pull

# Restart API service
sudo systemctl restart crypto-events-api

# Reload Nginx (if frontend changed)
sudo systemctl reload nginx
```

---

## 🔧 Part 10: Security Hardening (Optional but Recommended)

### Step 10.1: Setup Firewall

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### Step 10.2: Disable Root Login

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Find and change:
PermitRootLogin no
PasswordAuthentication no

# Save and restart SSH
sudo systemctl restart sshd
```

### Step 10.3: Setup Fail2Ban (Prevent Brute Force)

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Start and enable
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 🐛 Troubleshooting

### API Not Starting

```bash
# Check logs
sudo journalctl -u crypto-events-api -n 50

# Common issues:
# - MongoDB connection failed: Check MONGODB_URI in .env
# - Port already in use: Check if another process is using port 5000
# - Permission issues: Check file ownership
```

### Nginx Not Working

```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Common issues:
# - Syntax error in config
# - Port 80 already in use
# - File permissions
```

### Cron Job Not Running

```bash
# Check cron logs
grep CRON /var/log/syslog

# Test manually
cd ~/YOUR_REPO
source venv/bin/activate
python scraper_mongodb.py

# Check crontab
crontab -l
```

### Can't Connect to Server

```bash
# Check EC2 Security Group:
# - Port 22 (SSH) should be open
# - Port 80 (HTTP) should be open
# - Port 443 (HTTPS) should be open

# Check if services are running:
sudo systemctl status crypto-events-api
sudo systemctl status nginx
```

---

## 📝 Quick Reference Commands

### Service Management

```bash
# Start API
sudo systemctl start crypto-events-api

# Stop API
sudo systemctl stop crypto-events-api

# Restart API
sudo systemctl restart crypto-events-api

# View API logs
sudo journalctl -u crypto-events-api -f

# Restart Nginx
sudo systemctl restart nginx
```

### File Locations

```
Project: /home/ubuntu/YOUR_REPO
Logs: /var/log/nginx/
Service: /etc/systemd/system/crypto-events-api.service
Nginx Config: /etc/nginx/sites-available/crypto-events
Cron Jobs: crontab -e
Environment: /home/ubuntu/YOUR_REPO/.env
```

---

## 💰 Cost Optimization Tips

1. **Use Free Tier**: t2.micro is free for 12 months
2. **Stop When Not Needed**: Stop instance when testing (not terminated)
3. **Use Reserved Instances**: After free tier, save 30-60%
4. **Monitor Usage**: Set up billing alerts
5. **Optimize Images**: Compress images to reduce bandwidth

---

## 🔄 Backup Strategy

### Backup MongoDB

```bash
# MongoDB Atlas has automatic backups
# Configure in Atlas dashboard
```

### Backup EC2

```bash
# Create AMI (Amazon Machine Image)
# AWS Console → EC2 → Instances → Actions → Image → Create Image
```

### Backup Code

```bash
# Use GitHub for version control
cd ~/YOUR_REPO
git add .
git commit -m "Backup"
git push
```

---

## 📊 Performance Optimization

### Enable Gzip Compression

```bash
sudo nano /etc/nginx/nginx.conf

# Add in http block:
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;

# Restart Nginx
sudo systemctl restart nginx
```

### Add Caching Headers

Already included in the Nginx config above! ✅

---

## ✅ Deployment Checklist

- [ ] EC2 instance created and running
- [ ] SSH access working
- [ ] Python and dependencies installed
- [ ] Project files uploaded
- [ ] Environment variables configured
- [ ] API service running
- [ ] Cron job scheduled
- [ ] Nginx configured and running
- [ ] Frontend accessible via browser
- [ ] API endpoints responding
- [ ] SSL certificate installed (optional)
- [ ] Firewall configured
- [ ] Monitoring setup

---

## 🎉 Success!

Your crypto events app is now running on AWS EC2!

**Access your app:**
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
- **Gunicorn Documentation**: https://docs.gunicorn.org

---

## 🚀 Next Steps

1. ✅ Monitor logs for first 24 hours
2. ✅ Test cron job runs at midnight
3. ✅ Setup CloudWatch for monitoring (optional)
4. ✅ Configure automatic backups
5. ✅ Add custom domain with SSL
6. ✅ Share your app with the world! 🌍

---

**Total Setup Time**: 45-60 minutes

**Monthly Cost**: $0 (free tier) or ~$11-13 after

**Result**: Full-stack crypto events platform on AWS! 🎉
