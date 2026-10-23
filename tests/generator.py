import random
import string
from datetime import date, timedelta, datetime

def generate_booking_payload() -> dict:
    room_id = random.randint(1, 999)
    user_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    days_between = (date(2026, 12, 25) - date(2026, 1, 1)).days
    random_date = date(2026, 1, 1) + timedelta(days=random.randint(0, days_between))
    start_time = datetime.combine(random_date, datetime.min.time()).replace(hour=random.randint(9, 18))
    end_time = start_time + timedelta(days=random.randint(1, 5), hours=random.randint(1, 3))
    
    return {
        "room_id": room_id, 
        "user_name": user_name, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }

def generate_update_payload(original_payload: dict) -> dict:
    return {
        "room_id": original_payload["room_id"] + random.randint(50, 200),
        "user_name": f"updated_{generate_random_user_name()}",
        "start_time": generate_random_start_time(),
        "end_time": generate_random_end_time("2026-12-25")
    }

def generate_partial_update_payload(field_name: str) -> dict:
    if field_name == "room_id":
        return {"room_id": random.randint(100, 999)}
    elif field_name == "user_name":
        return {"user_name": f"patched_{generate_random_user_name()}"}
    elif field_name == "start_time":
        return {"start_time": generate_random_start_time()}
    elif field_name == "end_time":
        return {"end_time": generate_random_end_time("2026-12-25")}
    else:
        raise ValueError(f"Неизвестное поле: {field_name}")

def generate_random_user_name():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def generate_random_start_time():
    days_between = (date(2026, 12, 25) - date(2026, 1, 1)).days
    random_date = date(2026, 1, 1) + timedelta(days=random.randint(0, days_between))
    start_time = datetime.combine(random_date, datetime.min.time()).replace(hour=random.randint(9, 18))
    return start_time.isoformat()

def generate_random_end_time(start_time_str):
    start_time = datetime.fromisoformat(start_time_str)
    end_time = start_time + timedelta(days=random.randint(1, 5), hours=random.randint(1, 3))
    return end_time.isoformat()