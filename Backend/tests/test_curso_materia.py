import requests
import os

BASE = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:5000')


def create_sample_profesor():
    r = requests.post(f"{BASE}/api/profesores", json={
        "nombre": "Prof",
        "apellido": "Test",
        "cedula_prof": "1111"
    }, timeout=5)
    assert r.status_code == 201
    return r.json()['id_profesor']


def create_sample_materia():
    r = requests.post(f"{BASE}/api/materias", json={"nombre_materia": "MATTEST"}, timeout=5)
    assert r.status_code == 201
    return r.json()['id_materia']


def create_sample_curso():
    payload = {
        "nombre_curso": "CURSOTEST",
        "anio_escolar": "2026",
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31"
    }
    r = requests.post(f"{BASE}/api/cursos", json=payload, timeout=5)
    assert r.status_code == 201
    return r.json()['id_curso']


def test_add_and_update_asignaciones():
    curso_id = create_sample_curso()
    mat1 = create_sample_materia()
    mat2 = create_sample_materia()
    prof1 = create_sample_profesor()
    prof2 = create_sample_profesor()

    # asignar mat1 a prof1 y mat2 a prof2
    assignments = [
        {"id_materia": mat1, "id_profesor": prof1},
        {"id_materia": mat2, "id_profesor": prof2}
    ]
    r = requests.post(f"{BASE}/api/cursos/{curso_id}/materias", json=assignments, timeout=5)
    assert r.status_code == 200
    ids = r.json().get('ids', [])
    assert len(ids) == 2

    # verificar listado
    r2 = requests.get(f"{BASE}/api/cursos/{curso_id}/materias", timeout=5)
    assert r2.status_code == 200
    data = r2.json()
    assert any(d['id_materia'] == mat1 and d['id_profesor'] == prof1 for d in data)
    assert any(d['id_materia'] == mat2 and d['id_profesor'] == prof2 for d in data)

    # volver a enviar mat1 con prof2 para actualizar
    r3 = requests.post(f"{BASE}/api/cursos/{curso_id}/materias", json=[{"id_materia": mat1, "id_profesor": prof2}], timeout=5)
    assert r3.status_code == 200

    r4 = requests.get(f"{BASE}/api/cursos/{curso_id}/materias", timeout=5)
    assert r4.status_code == 200
    data2 = r4.json()
    # mat1 ahora debe referir prof2
    assert any(d['id_materia'] == mat1 and d['id_profesor'] == prof2 for d in data2)
    # sigue mat2-prof2
    assert any(d['id_materia'] == mat2 and d['id_profesor'] == prof2 for d in data2)

    # anular la primera asignación
    first_id = next(d['id_curso_materia'] for d in data2 if d['id_materia'] == mat1)
    r5 = requests.post(f"{BASE}/api/cursos/{curso_id}/materias/{first_id}/anular", timeout=5)
    assert r5.status_code == 200

    r6 = requests.get(f"{BASE}/api/cursos/{curso_id}/materias", timeout=5)
    assert any(d['id_curso_materia'] == first_id and d.get('anu_cur_mat') == 'X' for d in r6.json())
