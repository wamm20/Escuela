import requests
import os

BASE = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:5000')


def test_crud_materia():
    # crear materia
    url = f"{BASE}/api/materias"
    payload = {"nombre_materia": "MATEMATICAS"}
    r = requests.post(url, json=payload, timeout=5)
    assert r.status_code == 201
    data = r.json()
    assert 'id_materia' in data
    mid = data['id_materia']

    # leer lista y detalle
    r2 = requests.get(f"{BASE}/api/materias", timeout=5)
    assert r2.status_code == 200
    assert any(m['id_materia'] == mid for m in r2.json())

    r3 = requests.get(f"{BASE}/api/materias/{mid}", timeout=5)
    assert r3.status_code == 200
    assert r3.json().get('nombre_materia') == 'MATEMATICAS'

    # actualizar
    r4 = requests.put(f"{BASE}/api/materias/{mid}", json={"nombre_materia": "FISICA"}, timeout=5)
    assert r4.status_code == 200
    r5 = requests.get(f"{BASE}/api/materias/{mid}", timeout=5)
    assert r5.json().get('nombre_materia') == 'FISICA'

    # anular
    r6 = requests.delete(f"{BASE}/api/materias/{mid}", timeout=5)
    assert r6.status_code == 200
    r7 = requests.get(f"{BASE}/api/materias/{mid}", timeout=5)
    assert r7.status_code == 200
    assert r7.json().get('anu_mat') == 'X'
