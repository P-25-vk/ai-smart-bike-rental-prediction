"""
Test RDS PostgreSQL Connection
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "database": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
}

print("=" * 60)
print("  Testing RDS PostgreSQL Connection")
print("=" * 60)
print(f"\n🌍 Host: {DB_CONFIG['host']}")
print(f"🔢 Port: {DB_CONFIG['port']}")
print(f"💾 Database: {DB_CONFIG['database']}")
print(f"👤 User: {DB_CONFIG['user']}")
print()

try:
    print("🔌 Connecting to RDS...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("✅ Connection Successful!")
    print()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"📊 PostgreSQL Version:")
    print(f"   {version}")
    print()
    
    # Check if bike_rentals table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'bike_rentals'
        );
    """)
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM bike_rentals;")
        count = cursor.fetchone()[0]
        print(f"✅ Table 'bike_rentals' exists with {count:,} records")
    else:
        print("⚠️  Table 'bike_rentals' does not exist yet")
        print("   Run 'python db_insert.py' to create and populate it")
    
    cursor.close()
    conn.close()
    
    print()
    print("=" * 60)
    print("🎉 RDS Connection Test Passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Connection Failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("  - Check if endpoint, username, and password are correct")
    print("  - Verify security group allows inbound traffic on port 5432")
    print("  - Ensure RDS instance is publicly accessible")
    print("  - Check if your IP is allowed in the security group")
