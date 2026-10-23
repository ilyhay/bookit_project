import pytest
import allure

@allure.epic("Bookit API")
@allure.feature("Database Direct Operations")
@allure.story("CRUD Operations via DB")
class TestCRUDBookingInDB:

    @allure.title("Создание брони напрямую в БД и проверка коммита")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_booking_in_database(self, booking_payload, db_connection):
        with allure.step("Выполняем INSERT запрос напрямую в PostgreSQL"):
            cur = db_connection.cursor()
            try:
                cur.execute(
                    "INSERT INTO bookings (room_id, user_name, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING id",
                    (booking_payload["room_id"], booking_payload["user_name"], 
                     booking_payload["start_time"], booking_payload["end_time"])
                )
                # ВАЖНО: Сохраняем изменения!
                db_connection.commit()
                
                booking_id = cur.fetchone()[0]
                
                allure.attach(
                    f"Booking ID: {booking_id}\nRoom: {booking_payload['room_id']}\nUser: {booking_payload['user_name']}",
                    name="Created Record",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                assert booking_id is not None, "ID записи не был возвращен"
                
            finally:
                cur.close()
        
        with allure.step("Проверяем, что запись реально сохранилась в БД"):
            cur = db_connection.cursor()
            try:
                cur.execute("SELECT room_id, user_name, start_time, end_time FROM bookings WHERE id = %s", (booking_id,))
                db_record = cur.fetchone()
                
                assert db_record is not None, "Запись не найдена в базе данных"
                assert db_record[0] == booking_payload["room_id"]
                assert db_record[1] == booking_payload["user_name"]
                assert str(db_record[2]) == booking_payload["start_time"].replace("T", " ")
                assert str(db_record[3]) == booking_payload["end_time"].replace("T", " ")
                
            finally:
                cur.close()
        
        with allure.step("Очистка тестовых данных"):
            cur = db_connection.cursor()
            try:
                cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
                db_connection.commit()
            finally:
                cur.close()

    @allure.title("Полное обновление брони напрямую в БД")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_booking_in_database(self, booking_payload, db_connection):
        # Создаем тестовую запись
        with allure.step("Создаем тестовую бронь для обновления"):
            cur = db_connection.cursor()
            try:
                cur.execute(
                    "INSERT INTO bookings (room_id, user_name, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING id",
                    (booking_payload["room_id"], booking_payload["user_name"],
                     booking_payload["start_time"], booking_payload["end_time"])
                )
                db_connection.commit()
                booking_id = cur.fetchone()[0]
            finally:
                cur.close()
        
        # Обновляем запись
        with allure.step("Выполняем UPDATE запрос"):
            new_room_id = booking_payload["room_id"] + 100
            new_user_name = "updated_user"
            new_start_time = "2026-11-20T14:00:00"
            new_end_time = "2026-11-20T16:00:00"
            
            cur = db_connection.cursor()
            try:
                # ВАЖНО: Используем RETURNING, чтобы получить обновленные данные
                cur.execute(
                    """UPDATE bookings 
                       SET room_id = %s, user_name = %s, start_time = %s, end_time = %s 
                       WHERE id = %s 
                       RETURNING room_id, user_name, start_time, end_time""",
                    (new_room_id, new_user_name, new_start_time, new_end_time, booking_id)
                )
                db_connection.commit()
                
                updated_row = cur.fetchone()
                assert updated_row is not None, "UPDATE не вернул данные"
                
                allure.attach(
                    f"Updated values:\nRoom: {new_room_id}\nUser: {new_user_name}\nStart: {new_start_time}\nEnd: {new_end_time}",
                    name="Updated Record",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Проверяем, что данные обновились
                assert updated_row[0] == new_room_id
                assert updated_row[1] == new_user_name
                
            finally:
                cur.close()
        
        # Проверяем, что изменения сохранились
        with allure.step("Проверяем, что изменения сохранились в БД"):
            cur = db_connection.cursor()
            try:
                cur.execute("SELECT room_id, user_name FROM bookings WHERE id = %s", (booking_id,))
                db_record = cur.fetchone()
                
                assert db_record[0] == new_room_id
                assert db_record[1] == new_user_name
                
            finally:
                cur.close()
        
        # Очистка
        with allure.step("Очистка тестовых данных"):
            cur = db_connection.cursor()
            try:
                cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
                db_connection.commit()
            finally:
                cur.close()

    @allure.title("Удаление брони напрямую из БД")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_delete_booking_in_database(self, booking_payload, db_connection):
        # Создаем тестовую запись
        with allure.step("Создаем тестовую бронь для удаления"):
            cur = db_connection.cursor()
            try:
                cur.execute(
                    "INSERT INTO bookings (room_id, user_name, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING id",
                    (booking_payload["room_id"], booking_payload["user_name"],
                     booking_payload["start_time"], booking_payload["end_time"])
                )
                db_connection.commit()
                booking_id = cur.fetchone()[0]
            finally:
                cur.close()
        
        # Проверяем, что запись существует
        with allure.step("Проверяем, что запись существует перед удалением"):
            cur = db_connection.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM bookings WHERE id = %s", (booking_id,))
                count_before = cur.fetchone()[0]
                assert count_before == 1, "Запись не была создана"
            finally:
                cur.close()
        
        # Удаляем запись
        with allure.step("Выполняем DELETE запрос"):
            cur = db_connection.cursor()
            try:
                cur.execute("DELETE FROM bookings WHERE id = %s RETURNING id", (booking_id,))
                db_connection.commit()
                
                deleted_id = cur.fetchone()
                assert deleted_id is not None, "DELETE не вернул ID удаленной записи"
                assert deleted_id[0] == booking_id
                
            finally:
                cur.close()
        
        # Проверяем, что запись действительно удалена
        with allure.step("Проверяем, что запись удалена из БД"):
            cur = db_connection.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM bookings WHERE id = %s", (booking_id,))
                count_after = cur.fetchone()[0]
                
                assert count_after == 0, "Запись не была удалена из базы данных"
                
                allure.attach(
                    f"Booking ID {booking_id} успешно удален из БД",
                    name="Deletion Result",
                    attachment_type=allure.attachment_type.TEXT
                )
                
            finally:
                cur.close()