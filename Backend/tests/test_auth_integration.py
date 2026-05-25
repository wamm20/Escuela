import requests
import os

BASE = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:5000')


def test_login_success():
    url = f"{BASE}/api/login"
    payload = {"username": "wamm20@gmail.com", "password": "W1ll14m#$"}
    r = requests.post(url, json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data and isinstance(data['access_token'], str)


def test_login_fail_wrong_password():
    url = f"{BASE}/api/login"
    payload = {"username": "wamm20@gmail.com", "password": "wrong-password"}
    r = requests.post(url, json=payload, timeout=5)
    assert r.status_code == 401
    data = r.json()
    assert data.get('message') in ('invalid credentials', 'username and password required')
