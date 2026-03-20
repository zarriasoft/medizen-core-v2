import requests
import json

url = "http://localhost:8000/public/enroll"
data = {
    "first_name": "Maria",
    "last_name": "Zarria Castillo",
    "email": "mzarria@gmail.com",
    "phone": "958647556",
    "date_of_birth": "2026-02-24",
    "plan_name": "Intermedio"
}

print(f"Sending request to {url}")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
