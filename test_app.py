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

def test_health_ready(client):
    """Перевірка з'єднання з БД"""
    response = client.get('/health/ready')
    assert response.status_code == 200
    assert response.data == b"OK"

def test_create_item(client):
    """Перевірка створення предмета (POST)"""
    response = client.post('/items', json={"name": "Test Item", "quantity": 10})
    assert response.status_code == 201
    assert "id" in response.get_json()

def test_get_items(client):
    """Перевірка отримання списку предметів (GET)"""
    response = client.get('/items')
    assert response.status_code == 200
    assert type(response.get_json()) == list

def test_get_single_item_not_found(client):
    """Перевірка неіснуючого предмета"""
    response = client.get('/items/9999')
    assert response.status_code == 404