#!/bin/bash

# AWS EC2 Setup Script for Crypto Events App
# Run this script on your EC2 instance after connecting via SSH

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🚀 Crypto Events - AWS EC2 Setup Script             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    print_error "Please run this script as ubuntu user"
    exit 1
fi

print_info "Starting setup process..."
echo ""

# Step 1: Update system
print_info "Step 1/8: Updating system packages..."
sudo apt update -y
sudo apt upgrade -y
print_success "System updated"
echo ""

# Step 2: Install dependencies
print_info "Step 2/8: Installing dependencies..."
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git build-essential libssl-dev libffi-dev python3-dev unzip
print_success "Dependencies installed"
echo ""

# Step 3: Get project files
print_info "Step 3/8: Setting up project..."
echo "Choose an option:"
echo "1) Clone from GitHub"
echo "2) I'll upload files manually later"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    read -p "Enter your GitHub repository URL: " repo_url
    cd ~
    git clone "$repo_url" crypto-events
    cd crypto-events
    print_success "Repository cloned"
else
    mkdir -p ~/crypto-events
    cd ~/crypto-events
    print_info "Project directory created at ~/crypto-events"
    print_info "Upload your files using: scp -i your-key.pem -r * ubuntu@YOUR_IP:~/crypto-events/"
    read -p "Press Enter after uploading files..."
fi
echo ""

# Step 4: Setup Python environment
print_info "Step 4/8: Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
print_success "Python environment ready"
echo ""

# Step 5: Configure environment variables
print_info "Step 5/8: Configuring environment variables..."
read -p "Enter your MongoDB URI: " mongodb_uri

cat > .env << EOF
MONGODB_URI=$mongodb_uri
PORT=5000
API_HOST=0.0.0.0
PYTHON_VERSION=3.11.0
EOF

print_success "Environment variables configured"
echo ""

# Step 6: Test application
print_info "Step 6/8: Testing application..."
print_info "Testing scraper..."
python scraper_mongodb.py
print_success "Scraper test completed"
echo ""

# Step 7: Setup systemd service
print_info "Step 7/8: Setting up systemd service..."
PROJECT_DIR=$(pwd)

sudo tee /etc/systemd/system/crypto-events-api.service > /dev/null << EOF
[Unit]
Description=Crypto Events API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start crypto-events-api
sudo systemctl enable crypto-events-api
print_success "API service started"
echo ""

# Step 8: Setup cron job
print_info "Step 8/8: Setting up daily scraper cron job..."
(crontab -l 2>/dev/null; echo "0 0 * * * $PROJECT_DIR/venv/bin/python $PROJECT_DIR/scraper_mongodb.py >> $HOME/scraper.log 2>&1") | crontab -
print_success "Cron job configured"
echo ""

# Step 9: Configure Nginx
print_info "Configuring Nginx..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

sudo tee /etc/nginx/sites-available/crypto-events > /dev/null << EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    location / {
        root $PROJECT_DIR;
        index events_api.html;
        try_files \$uri \$uri/ /events_api.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root $PROJECT_DIR;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/crypto-events /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
print_success "Nginx configured"
echo ""

# Step 10: Update frontend API URL
print_info "Updating frontend API URL..."
if [ -f "events_api.js" ]; then
    sed -i "s|const API_BASE_URL = .*|const API_BASE_URL = '/api';|g" events_api.js
    print_success "events_api.js updated"
fi

if [ -f "list_event.js" ]; then
    sed -i "s|const API_BASE_URL = .*|const API_BASE_URL = '/api';|g" list_event.js
    print_success "list_event.js updated"
fi
echo ""

# Final status check
print_info "Checking service status..."
sudo systemctl status crypto-events-api --no-pager
echo ""

# Display summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  🎉 SETUP COMPLETE! 🎉                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
print_success "Your app is now running!"
echo ""
echo "📍 Access your app at:"
echo "   http://$PUBLIC_IP"
echo ""
echo "🔍 API Endpoints:"
echo "   http://$PUBLIC_IP/api/health"
echo "   http://$PUBLIC_IP/api/events"
echo "   http://$PUBLIC_IP/api/stats"
echo ""
echo "📊 Useful Commands:"
echo "   Check API status:  sudo systemctl status crypto-events-api"
echo "   View API logs:     sudo journalctl -u crypto-events-api -f"
echo "   View Nginx logs:   sudo tail -f /var/log/nginx/access.log"
echo "   View scraper logs: tail -f ~/scraper.log"
echo "   Restart API:       sudo systemctl restart crypto-events-api"
echo "   Restart Nginx:     sudo systemctl restart nginx"
echo ""
echo "⏰ Scraper runs daily at midnight UTC"
echo ""
echo "🔒 Next steps (optional):"
echo "   1. Setup SSL certificate with Let's Encrypt"
echo "   2. Configure custom domain"
echo "   3. Setup firewall (UFW)"
echo "   4. Enable monitoring"
echo ""
print_success "Deployment successful! 🚀"
