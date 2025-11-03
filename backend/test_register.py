import requests
import json

def test_register():
    url = "http://localhost:8000/register"
    data = {
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register() 