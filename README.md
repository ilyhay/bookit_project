# BookIt API

Микросервис для управления бронированиями помещений. Реализует полный CRUD-цикл с валидацией данных, проверкой уникальности слотов и прямым взаимодействием с PostgreSQL.

## Технологический стек
- **Backend:** Python 3.11, FastAPI, Uvicorn
- **Database:** PostgreSQL 14
- **Testing:** Pytest, HTTPX, Pytest-Cov, Allure, JSONSchema
- **Infrastructure:** Docker, Docker Compose, GitHub Actions (CI/CD)
- **Debugging:** Charles Proxy integration

---

## Быстрый старт

### 1. Клонирование и настройка окружения

```bash
git clone https://github.com/ilyhay/bookit_project.git
cd bookit_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Запуск через Docker
Убедитесь, что Docker запущен. Выполните в корне проекта:

```bash
docker-compose up -d --build
```

API будет доступен по адресу: `http://localhost:8000`
Интерактивная документация (Swagger): `http://localhost:8000/docs`

---

## Тестирование
Проект содержит комплексные интеграционные и E2E тесты.

Запуск тестов с отчетом о покрытии (Coverage):
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term -v
```
HTML-отчет о покрытии будет сгенерирован в папке `htmlcov/.`

### Запуск тестов с отчетом Allure

```bash
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

### Режим отладки сети (Charles Proxy)
Чтобы перехватывать трафик тестов через Charles Proxy:
1. Включите проксирование в Charles (Proxy -> Windows/macOS Proxy).
2. В файле `tests/.env` установите `USE_CHARLES=true`.
3. Запустите тесты. Трафик будет идти через `localhost.charlesproxy.com:8000`.

---

## API Endpoints

|Метод|Путь|Описание|
|------|-----|------|
|POST|/bookings|Создать новую бронь|
|GET|/bookings/{room_id}|Получить все брони для комнаты|
|PUT|/bookings/{booking_id}|Полное обновление брони|
|PATCH|/bookings/{booking_id}|Частичное обновление брони|
|DELETE|/bookings/{booking_id}|Удалить бронь|

---

## CI/CD
При каждом push в ветку `main` или `master` автоматически запускается GitHub Actions workflow, который:
1. Собирает Docker-образы.
2. Запускает тесты с измерением покрытия.
3. Генерирует и публикует актуальный Allure-отчет на GitHub Pages.

---