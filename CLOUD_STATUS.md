# Cloud Connection Status

## Current Status: LOCAL (Not Connected to Cloud)

Your application is currently running **locally** on your computer. Here's what you need to do to connect it to AWS Cloud:

---

## What's Working Now (LOCAL)

✅ Backend API running on `http://localhost:5000`  
✅ Frontend running on `http://localhost:3000`  
✅ ML Model loaded from local file: `backend/bike_model.pkl`  
✅ Dataset loaded from local file: `backend/bike_rental.csv`  
✅ No database connection (using CSV file directly)

---

## To Connect to AWS Cloud

### You Need:

1. **AWS Account** with billing enabled
2. **AWS S3 Bucket** for storing:
   - ML model (`bike_model.pkl`)
   - Dataset (`bike_rental.csv`)
3. **AWS RDS PostgreSQL Database** for storing bike rental data
4. **AWS Credentials** (Access Key ID and Secret Access Key)

---

## Setup Steps

### Step 1: Configure AWS Credentials

Edit `backend/.env` file and replace these values:

```env
# Your actual AWS credentials
AWS_ACCESS_KEY_ID=YOUR_ACTUAL_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_ACTUAL_SECRET_KEY
S3_BUCKET=your-bucket-name
AWS_REGION=ap-south-1

# Your actual RDS database endpoint
DB_HOST=your-rds-endpoint.ap-south-1.rds.amazonaws.com
DB_PASSWORD=your-actual-password
```

### Step 2: Create S3 Bucket and Upload Files

**Option A: Using Python Script**
```bash
cd backend
python upload_to_s3.py
```

**Option B: Using AWS Console**
- Login to AWS Console
- Create S3 bucket
- Upload `bike_model.pkl` to `models/` folder
- Upload `bike_rental.csv` to `dataset/` folder

### Step 3: Create RDS Database

1. Go to AWS RDS Console
2. Create PostgreSQL database
3. Note the endpoint URL
4. Update `DB_HOST` in `.env` file

### Step 4: Setup Database

```bash
cd backend
python db_insert.py
```

This will create tables and insert 15,000 records into your RDS database.

### Step 5: Restart Backend

Stop the current backend and restart:
```bash
cd backend
python app.py
```

The app will now:
- Download model from S3 (if not local)
- Download dataset from S3 (if not local)
- Connect to RDS database for data queries

---

## Files Created for You

📄 `backend/.env` - AWS configuration file (UPDATE THIS!)  
📄 `AWS_SETUP_GUIDE.md` - Detailed step-by-step guide  
📄 `backend/upload_to_s3.py` - Script to upload files to S3  
📄 `CLOUD_STATUS.md` - This file (status summary)

---

## Cost Estimate

**Free Tier (First 12 months):**
- S3: First 5 GB free
- RDS: 750 hours/month of db.t3.micro free
- Total: **$0/month** within free tier limits

**After Free Tier:**
- S3: ~$0.50/month (for small files)
- RDS db.t3.micro: ~$12-15/month
- Total: ~$13-16/month

---

## Important Notes

⚠️ **Security Warning:**
- Never commit `.env` file to Git
- Keep AWS credentials secure
- Don't share your Secret Access Key

⚠️ **Current State:**
- Your app is NOT connected to cloud yet
- Everything is running locally
- You need to follow setup steps above to connect to AWS

✅ **After Setup:**
- Model and data will be stored in S3
- Database records will be in RDS
- App can scale and be accessed from anywhere

---

## Need Help?

1. Read the detailed guide: `AWS_SETUP_GUIDE.md`
2. Check AWS documentation
3. Test connection: Run `python upload_to_s3.py` after configuring `.env`

---

## Quick Test

To check if AWS is configured:

```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('S3 Bucket:', os.getenv('S3_BUCKET')); print('RDS Host:', os.getenv('DB_HOST'))"
```

If you see "YOUR_..." values, you need to update `.env` file with real credentials.
