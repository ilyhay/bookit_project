import pytest
import httpx
import psycopg2
import os
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from generator import (generate_booking_payload, generate_update_payload, generate_partial_update_payload)
from fastapi.testclient import TestClient
import sys
import pathlib

dotenv_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

USE_CHARLES = os.getenv("USE_CHARLES", "false").lower() == "true"

if USE_CHARLES:
    BASE_URL = os.getenv("BASE_URL", "http://localhost.charlesproxy.com:8000")
    PROXIES = {
        "http://": f"http://{os.getenv('CHARLES_PROXY_HOST', '127.0.0.1')}:{os.getenv('CHARLES_PROXY_PORT', '8888')}",
        "https://": f"http://{os.getenv('CHARLES_PROXY_HOST', '127.0.0.1')}:{os.getenv('CHARLES_PROXY_PORT', '8888')}",
    }
    print(f"\n [Charles Mode] Трафик будет перехватываться через {PROXIES['http://']}")
else:
    BASE_URL = os.getenv("BASE_URL_DIRECT", "http://localhost:8000")
    PROXIES = None
    print(f"\n [Direct Mode] Прямое подключение к {BASE_URL}")


sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app import app

@pytest.fixture(scope="session")
def api_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"), 
        user=os.getenv("DB_USER"), 
        password=os.getenv("DB_PASS"), 
        host=os.getenv("DB_TEST_HOST"), 
        port=os.getenv("DB_PORT")
    )
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def booking_payload():
    return generate_booking_payload()

@pytest.fixture(scope="function")
def update_payload(booking_payload):
    return generate_update_payload(booking_payload)

@pytest.fixture(scope="function")
def patch_payload_user_name():
    return generate_partial_update_payload("user_name")

@pytest.fixture(scope="function")
def patch_payload_room_id():
    return generate_partial_update_payload("room_id")

@pytest.fixture(scope="function")
def existing_booking(api_client, booking_payload):
    # 1. SETUP: Делаем запрос на создание
    create_response = api_client.post("/bookings", json=booking_payload)
    assert create_response.status_code == 200, f"Не удалось создать тестовую бронь: {create_response.text}"

    created_data = create_response.json()
    booking_id = created_data["id"]

    # 2. YIELD: Передаем данные в тесты
    yield {
        "payload": booking_payload,
        "created_id": booking_id
    }

    # 3. TEARDOWN: Очистка после теста 
    try:
        delete_response = api_client.delete(f"/bookings/{booking_id}")
        if delete_response.status_code not in [200, 204]:
            print(f"Warning: Не удалось удалить тестовую бронь {booking_id}: {delete_response.text}")
    except Exception as e:
        print(f"Warning: Ошибка при удалении брони {booking_id}: {e}")
        
@pytest.fixture
def validate_response():
    def _validate(response, schema):
        try:
            validate(instance=response.json(), schema=schema)
        except ValidationError as e:
            pytest.fail(f"JSON Schema validation failed: {e.message}")
        return response.json()
    return _validate
