import requests
import os

BASE = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:5000')


def test_crud_curso():
    # crear curso
    url = f"{BASE}/api/cursos"
    payload = {
        "nombre_curso": "CIENCIAS",
        "anio_escolar": "2026",
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2026-12-15"
    }
    r = requests.post(url, json=payload, timeout=5)
    assert r.status_code == 201
    data = r.json()
    assert 'id_curso' in data
    cid = data['id_curso']

    # listado y detalle
    r2 = requests.get(f"{BASE}/api/cursos", timeout=5)
    assert r2.status_code == 200
    assert any(c['id_curso'] == cid for c in r2.json())

    r3 = requests.get(f"{BASE}/api/cursos/{cid}", timeout=5)
    assert r3.status_code == 200
    assert r3.json().get('nombre_curso') == 'CIENCIAS'

    # actualizar
    r4 = requests.put(f"{BASE}/api/cursos/{cid}", json={"nombre_curso": "HISTORIA", "estado_curso": "CERRADO"}, timeout=5)
    assert r4.status_code == 200
    r5 = requests.get(f"{BASE}/api/cursos/{cid}", timeout=5)
    assert r5.json().get('nombre_curso') == 'HISTORIA'
    assert r5.json().get('estado_curso') == 'CERRADO'

    # anular
    r6 = requests.delete(f"{BASE}/api/cursos/{cid}", timeout=5)
    assert r6.status_code == 200
    r7 = requests.get(f"{BASE}/api/cursos/{cid}", timeout=5)
    assert r7.json().get('anu_cur') == 'X'
