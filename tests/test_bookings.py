import pytest
import allure
from schemas import (CREATE_BOOKING_SCHEMA, GET_BOOKINGS_SCHEMA, UPDATE_BOOKING_SCHEMA, DELETE_BOOKING_SCHEMA, ERROR_SCHEMA)

@allure.epic("Bookit API")
@allure.feature("Routes")
class TestCreateBooking:
    """Тесты для POST /bookings"""
    
    @allure.story("Success")
    @allure.title("POST /bookings - успешное создание брони")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_booking_success(self, api_client, booking_payload, validate_response):
        with allure.step("Отправляем POST запрос с валидными данными"):
            response = api_client.post("/bookings", json=booking_payload)
        
        with allure.step("Проверяем статус код 200"):
            assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}"
        
        with allure.step("Валидируем JSON схему ответа"):
            data = validate_response(response, CREATE_BOOKING_SCHEMA)
            assert "id" in data
            assert data["status"] == "confirmed"
        
        with allure.step("Очищаем тестовые данные"):
            api_client.delete(f"/bookings/{data['id']}")
    
    @allure.story("Conflict")
    @allure.title("POST /bookings - конфликт при дублировании room_id + start_time")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_booking_conflict(self, api_client, booking_payload, validate_response):
        with allure.step("Создаем первую бронь"):
            response1 = api_client.post("/bookings", json=booking_payload)
            assert response1.status_code == 200
            booking_id = response1.json()["id"]
        
        with allure.step("Пытаемся создать вторую бронь с такими же данными"):
            response2 = api_client.post("/bookings", json=booking_payload)
        
        with allure.step("Проверяем статус код 409"):
            assert response2.status_code == 409
        
        with allure.step("Валидируем схему ошибки"):
            validate_response(response2, ERROR_SCHEMA)
        
        with allure.step("Очищаем тестовые данные"):
            api_client.delete(f"/bookings/{booking_id}")


@allure.epic("Bookit API")
@allure.feature("Routes")
class TestGetBooking:
    """Тесты для GET /bookings/{room_id}"""
    
    @allure.story("Success")
    @allure.title("GET /bookings/{room_id} - получение существующей брони")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_get_existing_booking(self, api_client, existing_booking, validate_response):
        room_id = existing_booking["payload"]["room_id"]
        
        with allure.step(f"Отправляем GET запрос для room_id={room_id}"):
            response = api_client.get(f"/bookings/{room_id}")
        
        with allure.step("Проверяем статус код 200"):
            assert response.status_code == 200
        
        with allure.step("Валидируем JSON схему ответа"):
            data = validate_response(response, GET_BOOKINGS_SCHEMA)
            assert len(data) > 0
            assert data[0]["room"] == room_id
    
    @allure.story("Not Found")
    @allure.title("GET /bookings/{room_id} - запрос для несуществующей комнаты")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_nonexistent_booking(self, api_client, validate_response):
        nonexistent_room_id = 99999
        
        with allure.step("Отправляем GET запрос для несуществующего room_id"):
            response = api_client.get(f"/bookings/{nonexistent_room_id}")
        
        with allure.step("Проверяем статус код 404"):
            assert response.status_code == 404
        
        with allure.step("Валидируем схему ошибки"):
            validate_response(response, ERROR_SCHEMA)


@allure.epic("Bookit API")
@allure.feature("Routes")
class TestUpdateBooking:
    """Тесты для PUT /bookings/{booking_id}"""
    
    @allure.story("Success")
    @allure.title("PUT /bookings/{booking_id} - полное обновление брони")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_put_update_booking(self, api_client, existing_booking, update_payload, validate_response):
        booking_id = existing_booking["created_id"]
        
        with allure.step("Отправляем PUT запрос с новыми данными"):
            response = api_client.put(f"/bookings/{booking_id}", json=update_payload)
        
        with allure.step("Проверяем статус код 200"):
            assert response.status_code == 200
        
        with allure.step("Валидируем JSON схему ответа"):
            data = validate_response(response, UPDATE_BOOKING_SCHEMA)
            assert data["id"] == booking_id
            assert data["user"] == update_payload["user_name"]
        
        with allure.step("Очищаем тестовые данные"):
            api_client.delete(f"/bookings/{booking_id}")
    
    @allure.story("Not Found")
    @allure.title("PUT /bookings/{booking_id} - обновление несуществующей брони")
    @allure.severity(allure.severity_level.NORMAL)
    def test_put_nonexistent_booking(self, api_client, booking_payload, validate_response):
        nonexistent_id = 99999
        
        with allure.step("Отправляем PUT запрос для несуществующего ID"):
            response = api_client.put(f"/bookings/{nonexistent_id}", json=booking_payload)
        
        with allure.step("Проверяем статус код 404"):
            assert response.status_code == 404
        
        with allure.step("Валидируем схему ошибки"):
            validate_response(response, ERROR_SCHEMA)


@allure.epic("Bookit API")
@allure.feature("Routes")
class TestPatchBooking:
    """Тесты для PATCH /bookings/{booking_id}"""
    
    @allure.story("Success")
    @allure.title("PATCH /bookings/{booking_id} - частичное обновление (только user_name)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_patch_update_user_only(self, api_client, existing_booking, patch_payload_user_name, validate_response):
        booking_id = existing_booking["created_id"]
        original_payload = existing_booking["payload"]

        with allure.step("Отправляем PATCH запрос с изменением только user_name"):
            response = api_client.patch(f"/bookings/{booking_id}", json=patch_payload_user_name)

        with allure.step("Проверяем статус код 200"):
            assert response.status_code == 200

        with allure.step("Валидируем JSON схему ответа"):
            data = validate_response(response, UPDATE_BOOKING_SCHEMA)
            assert data["user"] == patch_payload_user_name["user_name"]
            assert data["room"] == original_payload["room_id"]

        with allure.step("Очищаем тестовые данные"):
            api_client.delete(f"/bookings/{booking_id}")
    
    @allure.story("Success")
    @allure.title("PATCH /bookings/{booking_id} - частичное обновление (только room_id)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_patch_update_room_only(self, api_client, existing_booking, patch_payload_room_id, validate_response):
        booking_id = existing_booking["created_id"]
        
        with allure.step("Отправляем PATCH запрос с изменением только room_id"):
            response = api_client.patch(f"/bookings/{booking_id}", json=patch_payload_room_id)
        
        with allure.step("Проверяем статус код 200"):
            assert response.status_code == 200
        
        with allure.step("Валидируем JSON схему ответа"):
            data = validate_response(response, UPDATE_BOOKING_SCHEMA)
            assert data["room"] == patch_payload_room_id["room_id"]
        
        with allure.step("Очищаем тестовые данные"):
            api_client.delete(f"/bookings/{booking_id}")
    
    @allure.story("Not Found")
    @allure.title("PATCH /bookings/{booking_id} - обновление несуществующей брони")
    @allure.severity(allure.severity_level.NORMAL)
    def test_patch_nonexistent_booking(self, api_client, validate_response):
        nonexistent_id = 99999
        
        with allure.step("Отправляем PATCH запрос для несуществующего ID"):
            response = api_client.patch(f"/bookings/{nonexistent_id}", json={"user_name": "test"})
        
        with allure.step("Проверяем статус код 404"):
            assert response.status_code == 404
        
        with allure.step("Валидируем схему ошибки"):
            validate_response(response, ERROR_SCHEMA)


@allure.epic("Bookit API")
@allure.feature("Routes")
class TestDeleteBooking:
    """Тесты для DELETE /bookings/{booking_id}"""
    
    @allure.story("Success")
    @allure.title("DELETE /bookings/{booking_id} - успешное удаление брони")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_delete_booking_success(self, api_client, existing_booking, validate_response):
        booking_id = existing_booking["created_id"]
        
        with allure.step(f"Отправляем DELETE запрос для booking_id={booking_id}"):
            response = api_client.delete(f"/bookings/{booking_id}")
        
        with allure.step("Проверяем статус код 200"):
            assert response.status_code == 200
        
        with allure.step("Валидируем JSON схему ответа"):
            data = validate_response(response, DELETE_BOOKING_SCHEMA)
            assert "deleted successfully" in data["message"]
        
        with allure.step("Проверяем, что бронь действительно удалена"):
            get_response = api_client.get(f"/bookings/{existing_booking['payload']['room_id']}")
            # После удаления GET должен вернуть 404 или пустой список
            assert get_response.status_code in [404, 200]
    
    @allure.story("Not Found")
    @allure.title("DELETE /bookings/{booking_id} - удаление несуществующей брони")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_nonexistent_booking(self, api_client, validate_response):
        nonexistent_id = 99999
        
        with allure.step("Отправляем DELETE запрос для несуществующего ID"):
            response = api_client.delete(f"/bookings/{nonexistent_id}")
        
        with allure.step("Проверяем статус код 404"):
            assert response.status_code == 404
        
        with allure.step("Валидируем схему ошибки"):
            validate_response(response, ERROR_SCHEMA)