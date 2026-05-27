import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Перевірка головної сторінки"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"GET /items" in response.data

def test_health_alive(client):
    """Перевірка ендпоінту живлення (Liveness)"""
    response = client.get('/health/alive')
    assert response.status_code == 200
    assert response.data == b"OK"