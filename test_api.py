import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_auth_flow():
    # Login request
    login_url = f"{BASE_URL}/api/auth/login"
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print("1. Attempting login...")
    login_response = requests.post(login_url, json=login_data)
    print(f"Login Status Code: {login_response.status_code}")
    print(f"Login Response: {json.dumps(login_response.json(), indent=2)}\n")
    
    if login_response.status_code != 200:
        print("Login failed!")
        return
    
    # Get the access token
    access_token = login_response.json()['access_token']
    
    # Test JWT verification endpoint first
    test_jwt_url = f"{BASE_URL}/api/test-jwt"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("2. Testing JWT verification...")
    print(f"Request URL: {test_jwt_url}")
    print(f"Using headers: {json.dumps(headers, indent=2)}\n")
    
    test_response = requests.get(test_jwt_url, headers=headers)
    print(f"Test JWT Status Code: {test_response.status_code}")
    try:
        print(f"Test JWT Response: {json.dumps(test_response.json(), indent=2)}\n")
    except:
        print(f"Test JWT Response (raw): {test_response.text}\n")
    
    # Get current user info
    me_url = f"{BASE_URL}/api/users/me"
    print("3. Attempting to get current user info...")
    print(f"Request URL: {me_url}")
    
    me_response = requests.get(me_url, headers=headers)
    print(f"Me Status Code: {me_response.status_code}")
    try:
        print(f"Me Response: {json.dumps(me_response.json(), indent=2)}\n")
    except:
        print(f"Me Response (raw): {me_response.text}\n")

if __name__ == "__main__":
    test_auth_flow()