# AWS S3 and RDS Setup Guide

This guide will help you connect your Bike Rental Prediction app to AWS S3 and RDS.

## Prerequisites
- AWS Account
- AWS CLI installed (optional but recommended)
- Your AWS credentials (Access Key ID and Secret Access Key)

---

## Step 1: Create AWS S3 Bucket

1. **Login to AWS Console** → Go to S3 service
2. **Create a new bucket:**
   - Bucket name: `bike-rental-ml-assets` (or your preferred name)
   - Region: `ap-south-1` (Mumbai) or your preferred region
   - Keep default settings or adjust as needed
3. **Upload files to S3:**
   - Create folder: `models/`
   - Upload `bike_model.pkl` to `models/` folder
   - Create folder: `dataset/`
   - Upload `bike_rental.csv` to `dataset/` folder

**S3 Structure:**
```
bike-rental-ml-assets/
├── models/
│   └── bike_model.pkl
└── dataset/
    └── bike_rental.csv
```

---

## Step 2: Create AWS RDS PostgreSQL Database

1. **Login to AWS Console** → Go to RDS service
2. **Create database:**
   - Engine: PostgreSQL
   - Version: PostgreSQL 15 (or latest)
   - Templates: Free tier (for testing) or Production
   - DB instance identifier: `bike-rental-db`
   - Master username: `postgres`
   - Master password: [Create a secure password]
   - DB instance class: `db.t3.micro` (free tier eligible)
   - Storage: 20 GB (General Purpose SSD)
   - Public access: **Yes** (to access from your local machine)
   - VPC security group: Create new → Allow PostgreSQL (port 5432)

3. **Wait for database to be created** (5-10 minutes)

4. **Note your RDS endpoint:**
   - Example: `bike-rental-db.abc123xyz.ap-south-1.rds.amazonaws.com`

---

## Step 3: Configure Security Group for RDS

1. Go to **EC2 → Security Groups**
2. Find the security group attached to your RDS instance
3. **Edit inbound rules:**
   - Type: PostgreSQL
   - Port: 5432
   - Source: Your IP address (or `0.0.0.0/0` for testing - not recommended for production)

---

## Step 4: Get AWS Credentials

### Option A: Using IAM User (Recommended)

1. Go to **IAM → Users**
2. Create new user: `bike-rental-app`
3. Attach policies:
   - `AmazonS3FullAccess` (or create custom policy with read-only access)
   - `AmazonRDSFullAccess` (or create custom policy)
4. **Create access key:**
   - Go to Security credentials tab
   - Create access key
   - Download and save:
     - Access Key ID
     - Secret Access Key

### Option B: Using Root Account (Not recommended for production)
- Use your root account credentials

---

## Step 5: Update .env File

1. Open `backend/.env` file
2. Replace the placeholder values:

```env
# AWS S3 Configuration
S3_BUCKET=bike-rental-ml-assets
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# AWS RDS PostgreSQL Configuration
DB_HOST=bike-rental-db.abc123xyz.ap-south-1.rds.amazonaws.com
DB_NAME=bike_rental_db
DB_USER=postgres
DB_PASSWORD=YourSecurePassword123!
DB_PORT=5432

# App Configuration
ALLOWED_ORIGINS=*
ADMIN_KEY=your-secure-admin-key-here
```

---

## Step 6: Setup Database Schema and Insert Data

1. **Create database table:**
```bash
cd backend
python db_insert.py
```

This will:
- Connect to your RDS database
- Create the `bike_rentals` table
- Insert all 15,000 records from `bike_rental.csv`

---

## Step 7: Upload Files to S3 (Using AWS CLI - Optional)

If you have AWS CLI installed:

```bash
# Configure AWS CLI
aws configure
# Enter your Access Key ID, Secret Key, Region

# Upload model to S3
aws s3 cp backend/bike_model.pkl s3://bike-rental-ml-assets/models/bike_model.pkl

# Upload dataset to S3
aws s3 cp backend/bike_rental.csv s3://bike-rental-ml-assets/dataset/bike_rental.csv

# Verify uploads
aws s3 ls s3://bike-rental-ml-assets/models/
aws s3 ls s3://bike-rental-ml-assets/dataset/
```

---

## Step 8: Test the Connection

1. **Stop the current backend server** (if running)
2. **Restart the backend:**
```bash
cd backend
python app.py
```

3. **Check the logs:**
   - If S3 is configured: App will download model and dataset from S3
   - If RDS is configured: Database connections will use RDS

4. **Test the frontend:**
   - Open http://localhost:3000
   - Try making a prediction
   - Check if data is being saved to RDS

---

## Verification Checklist

- [ ] S3 bucket created and files uploaded
- [ ] RDS database created and accessible
- [ ] Security group allows PostgreSQL access (port 5432)
- [ ] `.env` file updated with correct credentials
- [ ] Database table created (`bike_rentals`)
- [ ] 15,000 records inserted into database
- [ ] Backend connects to S3 successfully
- [ ] Backend connects to RDS successfully
- [ ] Frontend works with cloud backend

---

## Troubleshooting

### S3 Connection Issues
- Check bucket name is correct
- Verify AWS credentials are valid
- Ensure IAM user has S3 read permissions
- Check bucket region matches `AWS_REGION` in `.env`

### RDS Connection Issues
- Verify RDS endpoint is correct
- Check security group allows inbound traffic on port 5432
- Ensure RDS instance is publicly accessible (for local testing)
- Verify database credentials (username/password)
- Check if RDS instance is in "Available" state

### Database Insert Errors
- Make sure PostgreSQL driver is installed: `pip install psycopg2-binary`
- Check if database name exists on RDS instance
- Verify CSV file exists locally before running `db_insert.py`

---

## Cost Considerations

**AWS Free Tier includes:**
- S3: 5 GB storage for 12 months
- RDS: 750 hours/month of db.t3.micro instance (12 months)
- RDS: 20 GB storage

**After free tier:**
- S3: ~$0.023/GB per month
- RDS db.t3.micro: ~$0.017/hour (~$12/month)

---

## Security Best Practices

1. **Never commit `.env` file to Git** (it's in `.gitignore`)
2. **Use IAM roles** instead of access keys when deploying to EC2
3. **Restrict S3 bucket access** (don't make it public)
4. **Use VPC** and private subnets for RDS in production
5. **Enable SSL/TLS** for database connections
6. **Rotate credentials** regularly
7. **Use AWS Secrets Manager** for storing sensitive credentials in production

---

## Next Steps

Once S3 and RDS are configured, you can:
1. Deploy the backend to AWS EC2 or Elastic Beanstalk
2. Deploy the frontend to AWS S3 + CloudFront or Amplify
3. Setup API Gateway for the backend
4. Configure custom domain with Route 53
5. Setup CloudWatch monitoring and alerts
6. Enable automated backups for RDS

---

For more information, refer to:
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [Project README](README.md)
