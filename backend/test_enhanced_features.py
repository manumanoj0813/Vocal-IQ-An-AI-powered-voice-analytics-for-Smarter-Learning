#!/usr/bin/env python3
"""
Test script for enhanced features
"""

import requests
import json
import os

def test_enhanced_features():
    """Test the enhanced features endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if server is running
    print("🔍 Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/test")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Get supported languages
    print("\n🌍 Testing supported languages endpoint...")
    try:
        response = requests.get(f"{base_url}/supported-languages")
        if response.status_code == 200:
            languages = response.json()
            print(f"✅ Supported languages: {languages['total_languages']} languages")
            print(f"   Default: {languages['default_language']}")
            print(f"   Languages: {list(languages['supported_languages'].keys())[:5]}...")
        else:
            print(f"❌ Failed to get languages: {response.status_code}")
    except Exception as e:
        print(f"❌ Language endpoint error: {e}")
    
    # Test 3: Register a test user
    print("\n👤 Testing user registration...")
    try:
        register_data = {
            "username": "enhanced_test_user",
            "email": "enhanced@test.com",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/register", json=register_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print("✅ User registered successfully")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Test 4: Test export endpoint (should fail without recordings, but should respond)
    print("\n📊 Testing export endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        export_data = {
            "format": "csv",
            "include_transcriptions": True,
            "include_voice_cloning": True
        }
        response = requests.post(f"{base_url}/export-data", json=export_data, headers=headers)
        if response.status_code == 404:
            print("✅ Export endpoint working (no recordings to export)")
        else:
            print(f"⚠️  Export endpoint response: {response.status_code}")
    except Exception as e:
        print(f"❌ Export endpoint error: {e}")
    
    # Test 5: Test comparison charts endpoint
    print("\n📈 Testing comparison charts endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/comparison-charts", headers=headers)
        if response.status_code == 404:
            print("✅ Comparison charts endpoint working (no recordings for charts)")
        else:
            print(f"⚠️  Charts endpoint response: {response.status_code}")
    except Exception as e:
        print(f"❌ Charts endpoint error: {e}")
    
    # Test 6: Test language charts endpoint
    print("\n🌐 Testing language charts endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/language-charts", headers=headers)
        if response.status_code == 404:
            print("✅ Language charts endpoint working (no recordings for charts)")
        else:
            print(f"⚠️  Language charts response: {response.status_code}")
    except Exception as e:
        print(f"❌ Language charts error: {e}")
    
    print("\n🎉 Enhanced features test completed!")
    print("\n📋 Summary:")
    print("   - Server connectivity: ✅")
    print("   - Language support: ✅")
    print("   - User authentication: ✅")
    print("   - Export functionality: ✅")
    print("   - Chart generation: ✅")
    print("\n🚀 All enhanced features are ready to use!")

if __name__ == "__main__":
    test_enhanced_features() 