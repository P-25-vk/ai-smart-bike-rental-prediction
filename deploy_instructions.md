# 🚀 Deployment Guide - Host Your App Online

## Option 1: Deploy to Render (FREE & Easy) ⭐ RECOMMENDED

### Prerequisites:
- GitHub account
- Render account (free): https://render.com

---

## Step 1: Push to GitHub

### If you don't have GitHub repo yet:

1. **Create GitHub repo**: https://github.com/new
   - Repository name: `bike-rental-prediction`
   - Keep it Public
   - Don't initialize with README
   - Click "Create repository"

2. **Push your code** (run these commands):

```bash
cd ai-smart-bike-rental-prediction
git init
git add .
git commit -m "Initial commit - Bike Rental Prediction App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bike-rental-prediction.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username**

---

## Step 2: Deploy Backend to Render

1. **Go to Render**: https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `bike-rental-backend`
   - **Region**: Singapore (closest to ap-south-1)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

5. **Add Environment Variables** (click "Advanced"):
   ```
   S3_BUCKET=bike-rental-ml-assets
   AWS_REGION=ap-south-1
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   ALLOWED_ORIGINS=*
   ```

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. **Copy your backend URL**: `https://bike-rental-backend.onrender.com`

---

## Step 3: Deploy Frontend to Render

1. Click **"New +"** → **"Static Site"**
2. Connect same GitHub repository
3. Configure:
   - **Name**: `bike-rental-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`

4. **Add Environment Variable**:
   ```
   REACT_APP_API_URL=https://bike-rental-backend.onrender.com
   ```

5. Click **"Create Static Site"**
6. Wait 5-10 minutes
7. **Your app is live!** 🎉

---

## ✅ After Deployment

Your app will be available at:
- **Frontend**: `https://bike-rental-frontend.onrender.com`
- **Backend**: `https://bike-rental-backend.onrender.com`

Anyone can access it from anywhere!

---

## Option 2: Deploy to AWS (More Complex)

### Architecture:
- **Frontend**: AWS S3 + CloudFront
- **Backend**: AWS EC2 or Elastic Beanstalk
- **Storage**: AWS S3 (already configured)

### Cost:
- S3 + CloudFront: ~$1-5/month
- EC2 t3.micro: ~$8-10/month
- Total: ~$10-15/month

### Steps:

#### A. Deploy Frontend to S3 + CloudFront

1. **Build frontend**:
```bash
cd frontend
npm run build
```

2. **Create S3 bucket for website**:
   - Go to S3 Console
   - Create bucket: `bike-rental-frontend`
   - Enable "Static website hosting"
   - Upload `build/` folder contents

3. **Create CloudFront distribution**:
   - Origin: Your S3 bucket
   - Enable HTTPS
   - Get CloudFront URL

#### B. Deploy Backend to EC2

1. **Launch EC2 instance**:
   - AMI: Amazon Linux 2
   - Instance type: t3.micro (free tier)
   - Open ports: 80, 443, 5000

2. **SSH to EC2 and setup**:
```bash
sudo yum update -y
sudo yum install python3 git -y
git clone https://github.com/YOUR_USERNAME/bike-rental-prediction.git
cd bike-rental-prediction/backend
pip3 install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Use Nginx as reverse proxy** (optional but recommended)

---

## Option 3: Deploy to Vercel + Railway

### Frontend on Vercel (Free):
1. Go to: https://vercel.com
2. Import your GitHub repo
3. Set Root Directory: `frontend`
4. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   ```
5. Deploy!

### Backend on Railway (Free tier):
1. Go to: https://railway.app
2. New Project → Deploy from GitHub
3. Select your repo
4. Set Root Directory: `backend`
5. Add environment variables (S3 credentials)
6. Deploy!

---

## 📊 Comparison

| Platform | Free Tier | Ease | Best For |
|----------|-----------|------|----------|
| **Render** | ✅ Yes | ⭐⭐⭐⭐⭐ Easy | Full-stack apps |
| **AWS** | ⚠️ Limited | ⭐⭐ Complex | Production apps |
| **Vercel+Railway** | ✅ Yes | ⭐⭐⭐⭐ Easy | Quick deploy |

---

## 🎯 My Recommendation

**Use Render** for now because:
1. ✅ Completely free (no credit card required)
2. ✅ Very easy to deploy
3. ✅ Automatic HTTPS
4. ✅ Auto-deploys on git push
5. ✅ Perfect for your app

Later, if you need more control, migrate to AWS.

---

## 🔧 Quick Render Deployment

**5-Minute Setup:**

1. Push code to GitHub
2. Sign up on Render
3. Connect GitHub repo
4. Deploy backend (Web Service)
5. Deploy frontend (Static Site)
6. Done! Your app is live 🎉

---

## 📝 Important Notes

**Before deploying:**
- ✅ Make sure `.env` is in `.gitignore` (don't commit secrets!)
- ✅ Use environment variables on hosting platform
- ✅ Update CORS settings if needed
- ✅ Test locally first

**After deployment:**
- Update your S3 bucket CORS settings if needed
- Monitor usage (stay within free tier)
- Set up custom domain (optional)

---

## 🆘 Need Help?

Choose which option you want and I'll guide you step-by-step!

1. **Render** - I'll help you deploy in 10 minutes
2. **AWS** - I'll guide you through the full setup
3. **Vercel + Railway** - Quick alternative option
