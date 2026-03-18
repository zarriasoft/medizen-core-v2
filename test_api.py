import requests

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("1. Login...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "demo@medizen.com", "password": "password"}) # use default or create user if needed. 
    if resp.status_code != 200:
        print("Login failed, response:", resp.text)
        # Try another password or just create a user
        print("Trying to register a test user...")
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test@medizen.com",
            "username": "test@medizen.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "role": "admin"
        })
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "test@medizen.com", "password": "password123"})
        if resp.status_code != 200:
            print("Login failed again!")
            return
            
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n2. Get Membership Plans...")
    resp = requests.get(f"{BASE_URL}/membership-plans/", headers=headers)
    print("GET Plans:", resp.status_code, resp.json())
    
    print("\n3. Create Membership Plan...")
    plan_data = {
        "name": "Test Script Plan",
        "price": "$50",
        "frequency": "Mensual",
        "features": "Feature 1, Feature 2",
        "color": "teal",
        "is_popular": True,
        "is_active": True
    }
    resp = requests.post(f"{BASE_URL}/membership-plans/", headers=headers, json=plan_data)
    print("POST Plan:", resp.status_code, resp.json())
    
    if resp.status_code == 200:
        plan_id = resp.json()["id"]
        print(f"\n4. Delete Membership Plan ({plan_id})...")
        resp = requests.delete(f"{BASE_URL}/membership-plans/{plan_id}", headers=headers)
        print("DELETE Plan:", resp.status_code, resp.json())
        
        print("\n5. Get Membership Plans after delete...")
        resp = requests.get(f"{BASE_URL}/membership-plans/", headers=headers)
        print("GET Plans:", resp.status_code, resp.json())

if __name__ == "__main__":
    test_api()
