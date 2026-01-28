# ⚡ AWS EC2 Quick Start - Windows Users

Deploy your crypto events app on AWS EC2 from Windows in 30 minutes.

---

## 🎯 What You Need

- ✅ Windows 10/11
- ✅ PowerShell (built-in)
- ✅ AWS Account
- ✅ MongoDB Atlas connection string
- ✅ 30 minutes

---

## 🚀 Quick Deploy (30 minutes)

### 1️⃣ Create EC2 Instance (5 min)

1. **Login**: https://console.aws.amazon.com
2. **Go to EC2** → Launch Instance
3. **Configure**:
   ```
   Name: crypto-events-server
   OS: Ubuntu Server 22.04 LTS
   Instance Type: t2.micro (Free tier)
   Key Pair: Create new → Download .pem file
   Network: ✅ Allow SSH, HTTP, HTTPS
   Storage: 30 GB
   ```
4. **Launch** → Wait 2 minutes
5. **Note** your Public IP address

---

### 2️⃣ Connect from Windows (5 min)

**Open PowerShell:**

```powershell
# Navigate to Downloads
cd $env:USERPROFILE\Downloads

# Set key permissions
icacls.exe crypto-events-key.pem /reset
icacls.exe crypto-events-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe crypto-events-key.pem /inheritance:r

# Connect to EC2
ssh -i crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
```

**If SSH not found:**
- Settings → Apps → Optional Features
- Add "OpenSSH Client"

---

### 3️⃣ Setup Server (15 min)

**On EC2 (after SSH connection):**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git unzip

# Upload your files (see Step 4)
```

---

### 4️⃣ Upload Files from Windows (5 min)

**Option A: Use Script (Recommended)**

1. **Edit** `windows-upload-files.ps1`:
   - Set `$EC2_IP` to your EC2 IP
   - Set `$PROJECT_PATH` to `D:\events_scrapper`
2. **Run** in PowerShell:
   ```powershell
   .\windows-upload-files.ps1
   ```

**Option B: Manual Upload**

```powershell
# Create zip
Compress-Archive -Path D:\events_scrapper\* -DestinationPath crypto-events.zip

# Upload
scp -i $env:USERPROFILE\Downloads\crypto-events-key.pem crypto-events.zip ubuntu@YOUR_PUBLIC_IP:~/
```

**Then on EC2:**

```bash
# Unzip
unzip crypto-events.zip -d crypto-events
cd crypto-events
```

---

### 5️⃣ Configure & Deploy (10 min)

**On EC2:**

```bash
# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure environment
nano .env
# Add:
# MONGODB_URI=your_mongodb_uri
# PORT=5000
# Save: Ctrl+O, Enter, Ctrl+X

# Create systemd service
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
WorkingDirectory=/home/ubuntu/crypto-events
Environment="PATH=/home/ubuntu/crypto-events/venv/bin"
EnvironmentFile=/home/ubuntu/crypto-events/.env
ExecStart=/home/ubuntu/crypto-events/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl start crypto-events-api
sudo systemctl enable crypto-events-api
```

**Configure Nginx:**

```bash
sudo nano /etc/nginx/sites-available/crypto-events
```

**Add:**

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location / {
        root /home/ubuntu/crypto-events;
        index events_api.html;
        try_files $uri $uri/ /events_api.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg)$ {
        root /home/ubuntu/crypto-events;
        expires 30d;
    }
}
```

**Enable:**

```bash
sudo ln -s /etc/nginx/sites-available/crypto-events /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

**Setup cron job:**

```bash
crontab -e
# Add:
0 0 * * * /home/ubuntu/crypto-events/venv/bin/python /home/ubuntu/crypto-events/scraper_mongodb.py >> /home/ubuntu/scraper.log 2>&1
```

---

### 6️⃣ Test from Windows (2 min)

**Open browser:**
```
http://YOUR_PUBLIC_IP
```

**Test API in PowerShell:**
```powershell
curl http://YOUR_PUBLIC_IP/api/health
curl http://YOUR_PUBLIC_IP/api/events
```

---

## ✅ Success Checklist

- [ ] EC2 instance running
- [ ] Connected via SSH from Windows
- [ ] Files uploaded
- [ ] Services running
- [ ] Website loads in browser
- [ ] Events display correctly

---

## 🔧 Windows Helper Scripts

### Connect to EC2

**Save as `connect-ec2.ps1`:**

```powershell
$EC2_IP = "YOUR_PUBLIC_IP"
$KEY_PATH = "$env:USERPROFILE\Downloads\crypto-events-key.pem"
ssh -i $KEY_PATH ubuntu@$EC2_IP
```

**Run:**
```powershell
.\connect-ec2.ps1
```

### Open Website

**Save as `open-website.ps1`:**

```powershell
Start-Process "http://YOUR_PUBLIC_IP"
```

---

## 🌐 Add Custom Domain (Optional)

### On Hostinger:

1. **DNS Settings** → Add A Record:
   ```
   Type: A
   Name: events
   Points to: YOUR_EC2_PUBLIC_IP
   TTL: 3600
   ```

### On EC2:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL
sudo certbot --nginx -d events.yourdomain.com
```

**Test from Windows:**
```
https://events.yourdomain.com
```

---

## 🐛 Troubleshooting

### SSH not working?

```powershell
# Enable OpenSSH Client
# Settings → Apps → Optional Features → Add "OpenSSH Client"
```

### Permission denied?

```powershell
# Fix key permissions
cd $env:USERPROFILE\Downloads
icacls.exe crypto-events-key.pem /reset
icacls.exe crypto-events-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe crypto-events-key.pem /inheritance:r
```

### Can't upload files?

**Use WinSCP (GUI):**
1. Download: https://winscp.net/
2. Protocol: SFTP
3. Host: YOUR_PUBLIC_IP
4. User: ubuntu
5. Key: crypto-events-key.ppk (convert .pem with PuTTYgen)

---

## 📊 Useful Commands

### From Windows PowerShell

```powershell
# Connect to EC2
ssh -i $env:USERPROFILE\Downloads\crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP

# Upload file
scp -i $env:USERPROFILE\Downloads\crypto-events-key.pem file.txt ubuntu@YOUR_PUBLIC_IP:~/

# Test API
curl http://YOUR_PUBLIC_IP/api/health

# Open website
Start-Process "http://YOUR_PUBLIC_IP"
```

### On EC2 Server

```bash
# Check services
sudo systemctl status crypto-events-api
sudo systemctl status nginx

# View logs
sudo journalctl -u crypto-events-api -f
tail -f ~/scraper.log

# Restart services
sudo systemctl restart crypto-events-api
sudo systemctl restart nginx
```

---

## 💡 Pro Tips

1. **Windows Terminal**: Better than PowerShell
   - Download from Microsoft Store

2. **VS Code Remote SSH**: Edit files directly on EC2
   - Install "Remote - SSH" extension
   - Connect to EC2 from VS Code

3. **Create Shortcuts**: Save PowerShell scripts for quick access

4. **WinSCP**: GUI for file transfer
   - Easier than command line

---

## 📚 Full Guides

- **Detailed Guide**: `AWS_DEPLOYMENT_WINDOWS.md`
- **Helper Scripts**: `windows-connect-ec2.ps1`, `windows-upload-files.ps1`
- **Comparison**: `DEPLOYMENT_COMPARISON.md`

---

## 🎉 You're Done!

Your app is now live on AWS EC2, deployed from Windows!

**Access**: `http://YOUR_PUBLIC_IP`

**With SSL**: `https://events.yourdomain.com`

**Total Time**: 30 minutes

**Cost**: $0 (free tier for 12 months)

---

**Need help?** See `AWS_DEPLOYMENT_WINDOWS.md` for detailed instructions.
