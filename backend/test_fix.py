from fastapi.testclient import TestClient
from main import app

def test_timeseries():
    client = TestClient(app)
    print("Testing /api/timeseries/chn...")
    response = client.get("/api/timeseries/chn")
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(f"Data points: {len(data['data'])}")
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_timeseries()
