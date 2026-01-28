# ⚡ AWS EC2 Quick Start - Deploy in 30 Minutes

The fastest way to deploy your crypto events app on AWS EC2.

---

## 🎯 What You'll Get

- ✅ Full-stack app on single EC2 instance
- ✅ Flask API with Gunicorn
- ✅ Nginx serving frontend + reverse proxy
- ✅ Automated daily scraping
- ✅ Free tier eligible (first 12 months)

---

## 💰 Cost

- **First 12 months**: $0 (AWS Free Tier)
- **After free tier**: ~$11-13/month

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

### 2️⃣ Connect to Server (2 min)

**Mac/Linux:**
```bash
chmod 400 crypto-events-key.pem
ssh -i crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
```

**Windows:**
- Use PuTTY with your .ppk key

---

### 3️⃣ Run Setup Script (20 min)

**Option A: Automated Setup (Recommended)**

```bash
# Download setup script
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/aws_setup_script.sh

# Make executable
chmod +x aws_setup_script.sh

# Run script
./aws_setup_script.sh

# Follow the prompts:
# - Enter GitHub repo URL (or upload files manually)
# - Enter MongoDB URI
# - Wait for setup to complete
```

**Option B: Manual Setup**

Follow the detailed guide in `AWS_DEPLOYMENT_GUIDE.md`

---

### 4️⃣ Test Your App (3 min)

**Open browser:**
```
http://YOUR_PUBLIC_IP
```

**Test API:**
```bash
curl http://YOUR_PUBLIC_IP/api/health
curl http://YOUR_PUBLIC_IP/api/events
```

---

## ✅ Success Checklist

- [ ] EC2 instance running
- [ ] Can SSH into server
- [ ] API service running
- [ ] Nginx serving frontend
- [ ] Website loads in browser
- [ ] Events display correctly
- [ ] Cron job scheduled

---

## 🔧 Useful Commands

```bash
# Check API status
sudo systemctl status crypto-events-api

# View API logs
sudo journalctl -u crypto-events-api -f

# Restart API
sudo systemctl restart crypto-events-api

# Restart Nginx
sudo systemctl restart nginx

# View Nginx logs
sudo tail -f /var/log/nginx/access.log

# View scraper logs
tail -f ~/scraper.log

# Test scraper manually
cd ~/crypto-events
source venv/bin/activate
python scraper_mongodb.py
```

---

## 🌐 Add Custom Domain (Optional)

### On Hostinger DNS:

```
Type: A Record
Name: events (or @ for root)
Points to: YOUR_EC2_PUBLIC_IP
TTL: 3600
```

### On EC2 Server:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d events.yourdomain.com

# Follow prompts and choose redirect HTTP to HTTPS
```

**Done!** Your site is now at `https://events.yourdomain.com` 🎉

---

## 🐛 Troubleshooting

### Can't connect to EC2?
- Check Security Group allows SSH (port 22)
- Verify key file permissions: `chmod 400 key.pem`
- Check you're using correct IP address

### API not starting?
```bash
# Check logs
sudo journalctl -u crypto-events-api -n 50

# Common fixes:
# - Verify MongoDB URI in .env
# - Check port 5000 not in use
# - Restart service
```

### Website not loading?
```bash
# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check logs
sudo tail -f /var/log/nginx/error.log
```

### Cron job not running?
```bash
# Check crontab
crontab -l

# Test manually
cd ~/crypto-events
source venv/bin/activate
python scraper_mongodb.py
```

---

## 📊 Monitoring

### Check Service Health

```bash
# API service
sudo systemctl status crypto-events-api

# Nginx
sudo systemctl status nginx

# Disk space
df -h

# Memory usage
free -h

# CPU usage
top
```

### View Logs

```bash
# API logs (live)
sudo journalctl -u crypto-events-api -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Scraper logs
tail -f ~/scraper.log
```

---

## 🔄 Update Your App

```bash
# Pull latest changes
cd ~/crypto-events
git pull

# Restart services
sudo systemctl restart crypto-events-api
sudo systemctl reload nginx
```

---

## 🔒 Security (Recommended)

### Setup Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Check status
sudo ufw status
```

### Install Fail2Ban

```bash
# Prevent brute force attacks
sudo apt install -y fail2ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 💡 Pro Tips

1. **Elastic IP**: Assign a static IP so it doesn't change on restart
2. **CloudWatch**: Setup monitoring and alerts
3. **Backups**: Create AMI snapshots regularly
4. **Auto-scaling**: Add load balancer for high traffic
5. **RDS**: Use AWS RDS instead of MongoDB Atlas (optional)

---

## 📦 What's Installed

```
✅ Ubuntu 22.04 LTS
✅ Python 3.11
✅ Nginx (web server)
✅ Gunicorn (WSGI server)
✅ Systemd service (auto-start)
✅ Cron job (daily scraping)
✅ Git
✅ Virtual environment
```

---

## 🎯 Architecture

```
Internet
    ↓
Nginx (Port 80/443)
    ├── Frontend (HTML/CSS/JS)
    └── /api/* → Gunicorn (Port 5000)
            ↓
        Flask API
            ↓
        MongoDB Atlas
```

---

## 💰 Cost Breakdown

### Free Tier (12 months)
```
EC2 t2.micro:     750 hrs/month  = $0
Storage (30 GB):  30 GB          = $0
Data Transfer:    15 GB/month    = $0
MongoDB Atlas:    512 MB         = $0
────────────────────────────────────
Total:                             $0/month ✅
```

### After Free Tier
```
EC2 t2.micro:     ~$8-10/month
Storage (30 GB):  ~$3/month
Data Transfer:    ~$1/month
MongoDB Atlas:    $0 (free tier)
────────────────────────────────────
Total:            ~$12-14/month
```

---

## 🆚 AWS vs Render Comparison

| Feature | AWS EC2 | Render |
|---------|---------|--------|
| **Cost (Free)** | 12 months | Forever (with limits) |
| **Cost (Paid)** | ~$12/month | $7/month |
| **Control** | Full control | Limited |
| **Setup** | 30 minutes | 15 minutes |
| **Maintenance** | Manual | Automatic |
| **Scaling** | Manual | Automatic |
| **SSL** | Manual (Certbot) | Automatic |
| **Best For** | Learning, Full control | Quick deploy, Easy |

---

## 📚 Next Steps

1. ✅ Monitor logs for 24 hours
2. ✅ Test cron job at midnight
3. ✅ Setup custom domain + SSL
4. ✅ Configure backups
5. ✅ Setup CloudWatch monitoring
6. ✅ Optimize performance
7. ✅ Share your app! 🌍

---

## 📞 Support

- **Detailed Guide**: See `AWS_DEPLOYMENT_GUIDE.md`
- **AWS Docs**: https://docs.aws.amazon.com
- **Ubuntu Guide**: https://ubuntu.com/server/docs
- **Nginx Docs**: https://nginx.org/en/docs

---

## 🎉 You're Done!

Your crypto events app is now running on AWS EC2!

**Access**: `http://YOUR_PUBLIC_IP`

**With SSL**: `https://events.yourdomain.com`

**Total Time**: 30 minutes

**Cost**: $0 (free tier) or ~$12/month

**Result**: Professional full-stack app on AWS! 🚀

---

**Pro Tip**: Save your EC2 public IP and SSH command for easy access:

```bash
# Save this command
ssh -i ~/crypto-events-key.pem ubuntu@YOUR_PUBLIC_IP
```
