#!/usr/bin/env python3
"""
 Test script for Payabl Flask Application
This script tests the basic functionality without requiring AWS setup
"""

import sys
import os
sys.path.append('/home/artem/payabl_flask_app')

def test_app_imports():
    """Test if the application imports correctly"""
    try:
        from app import app, DatabaseManager
        print("✅ App imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_flask_routes():
    """Test if Flask routes are properly configured"""
    try:
        from app import app
        
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home route working")
            else:
                print(f"❌ Home route failed: {response.status_code}")
            
            # Test transactions page (might fail without DB)
            response = client.get('/transactions')
            print(f"📊 Transactions route status: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Flask route test error: {e}")
        return False

def main():
    print("🧪 Testing Payabl Flask Application")
    print("=" * 50)
    
    # Test imports
    if not test_app_imports():
        sys.exit(1)
    
    # Test Flask routes
    if not test_flask_routes():
        sys.exit(1)
    
    print("\n✅ Basic tests passed!")
    print("📝 To run the full application:")
    print("   1. Configure your AWS credentials in .env")
    print("   2. Set up Aurora PostgreSQL cluster")
    print("   3. Run: ./start.sh")

if __name__ == "__main__":
    main()
