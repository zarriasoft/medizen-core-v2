import requests

# Test creating a membership plan on the local and production backends

prod_url = "https://medizen-backend.onrender.com/membership-plans/"

data = {
    "name": "Test Plan",
    "price": "100",
    "frequency": "mensual",
    "features": "Feature 1, Feature 2",
    "color": "teal",
    "is_popular": False
}

print("Testing Production Backend...")
try:
    response = requests.post(prod_url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
