import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

def test():
    print("Testing API for booking appointment...")

    login_data = urllib.parse.urlencode({
        "username": "zarria@gmail.com",
        "password": "123456"
    }).encode("utf-8")

    try:
        req_login = urllib.request.Request("http://localhost:8000/auth/login/patient", data=login_data)
        with urllib.request.urlopen(req_login) as response:
            res_login = json.loads(response.read().decode())
            token = res_login["access_token"]

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"Obteniendo disponibilidad para {target_date}...")

        req_avail = urllib.request.Request(f"http://localhost:8000/me/appointments/availability?target_date={target_date}", headers=headers)
        with urllib.request.urlopen(req_avail) as response:
            slots = json.loads(response.read().decode())

        print(f"Slots disponibles: {len(slots)}")
        if not slots:
            print("No hay slots!")
            return

        slot = slots[0]
        start_time = slot["start_time"]

        print(f"Intentando reservar el slot {start_time}...")

        book_data = json.dumps({
            "appointment_date": f"{target_date}T{start_time}",
            "notes": "Test automátizado"
        }).encode("utf-8")

        req_book = urllib.request.Request("http://localhost:8000/me/appointments", data=book_data, headers=headers)
        try:
            with urllib.request.urlopen(req_book) as response:
                print(f"Status Code: {response.status}")
                print(f"Respuesta: {response.read().decode()}")
        except urllib.error.HTTPError as e:
            print(f"HTTPError Status Code: {e.code}")
            print(f"Respuesta de Error: {e.read().decode()}")

    except Exception as e:
        print("Error en el script:", e)

if __name__ == "__main__":
    test()
