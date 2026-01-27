"""
Quick test to verify MongoDB Atlas connection
"""

from pymongo import MongoClient
import sys

# Your connection string
MONGODB_URI = 'mongodb+srv://admin:BGfaJ003nDZIFIdT@cluster0.c9yuy9y.mongodb.net/?appName=Cluster0'

print("🔍 Testing MongoDB Atlas connection...")
print(f"📡 Connecting to: cluster0.c9yuy9y.mongodb.net")
print()

try:
    # Try to connect with longer timeout
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    
    # Test the connection
    print("⏳ Attempting connection (10 second timeout)...")
    client.server_info()
    
    print("✅ SUCCESS! Connected to MongoDB Atlas!")
    print()
    
    # Show database info
    print("📊 Database Information:")
    print(f"   Server: {client.address}")
    print(f"   Databases: {client.list_database_names()}")
    
    client.close()
    print()
    print("🎉 Your MongoDB Atlas is configured correctly!")
    print("✅ You can now run: python setup_mongodb_simple.py")
    
except Exception as e:
    print("❌ CONNECTION FAILED!")
    print()
    print(f"Error: {e}")
    print()
    print("🔧 Possible issues:")
    print()
    print("1. Network Access not configured:")
    print("   → Go to MongoDB Atlas → Network Access")
    print("   → Click 'Add IP Address'")
    print("   → Click 'Allow Access from Anywhere'")
    print("   → Click 'Confirm'")
    print()
    print("2. Wrong username or password:")
    print("   → Username: admin")
    print("   → Password: Rr1IHSMM3rKHKC2p")
    print("   → Check in 'Database Access' section")
    print()
    print("3. Cluster not ready:")
    print("   → Wait a few minutes for cluster to be fully active")
    print("   → Check cluster status in MongoDB Atlas dashboard")
    print()
    sys.exit(1)

input("\nPress Enter to exit...")
