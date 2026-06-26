#!/bin/bash
# ============================================================
#  AWS EC2 Deployment Script
#  AI-Powered Smart Bike Rental Demand Prediction System
#  Run this on a fresh Ubuntu 22.04 EC2 instance
# ============================================================
set -e

APP_DIR="/home/ubuntu/bike-rental"
REPO_URL="https://github.com/P-25-vk/ai-smart-bike-rental-prediction.git"

echo "=============================="
echo " 1. System Update & Dependencies"
echo "=============================="
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y python3.11 python3.11-venv python3-pip \
    nodejs npm nginx git curl unzip awscli

echo "=============================="
echo " 2. Clone / Pull Project"
echo "=============================="
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR" && git pull
else
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

echo "=============================="
echo " 3. Backend Setup"
echo "=============================="
cd "$APP_DIR/backend"

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn python-dotenv

# Copy .env (must exist on the server already, or create it)
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edit /home/ubuntu/bike-rental/backend/.env with your credentials!"
fi

# Load env vars
export $(grep -v '^#' .env | xargs)

# Generate dataset if not present
if [ ! -f bike_rental.csv ]; then
    echo "Generating dataset..."
    python generate_dataset.py
fi

# Train model if not present
if [ ! -f bike_model.pkl ]; then
    echo "Training model (this takes ~2 mins)..."
    python train_model.py
fi

# Upload model and dataset to S3
if [ -n "$S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp bike_rental.csv s3://$S3_BUCKET/dataset/ --region $AWS_REGION || true
    aws s3 cp bike_model.pkl  s3://$S3_BUCKET/models/  --region $AWS_REGION || true
fi

deactivate

echo "=============================="
echo " 4. Frontend Build"
echo "=============================="
cd "$APP_DIR/frontend"

# Set production API URL (replace with your EC2 public IP or domain)
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
echo "REACT_APP_API_URL=http://$EC2_IP:5000" > .env

npm install
npm run build

echo "=============================="
echo " 5. Gunicorn Service"
echo "=============================="
sudo cp "$APP_DIR/deploy/gunicorn.service" /etc/systemd/system/bikerental.service
sudo systemctl daemon-reload
sudo systemctl enable bikerental
sudo systemctl restart bikerental
echo "Gunicorn status:"
sudo systemctl status bikerental --no-pager

echo "=============================="
echo " 6. Nginx Configuration"
echo "=============================="
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/bikerental
sudo ln -sf /etc/nginx/sites-available/bikerental /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "=============================="
echo " 7. Firewall"
echo "=============================="
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
sudo ufw --force enable

echo ""
echo "✅ Deployment Complete!"
echo "   Frontend: http://$EC2_IP"
echo "   Backend:  http://$EC2_IP:5000"
echo ""
echo "📋 Next steps:"
echo "   1. Edit /home/ubuntu/bike-rental/backend/.env with DB credentials"
echo "   2. Set up RDS PostgreSQL and run: python db_insert.py"
echo "   3. Point a domain to this IP and add SSL with: sudo certbot --nginx"
