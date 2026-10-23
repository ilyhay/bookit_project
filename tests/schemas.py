# Схема ответа POST /bookings
CREATE_BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "status": {"type": "string", "enum": ["confirmed"]}
    },
    "required": ["id", "status"]
}

# Схема ответа GET /bookings/{room_id}
GET_BOOKINGS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "room": {"type": "integer"},
            "user": {"type": "string"},
            "start": {"type": "string"},
            "end": {"type": "string"}
        },
        "required": ["id", "room", "user", "start", "end"]
    }
}

# Схема ответа PUT/PATCH
UPDATE_BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "room": {"type": "integer"},
        "user": {"type": "string"},
        "start": {"type": "string"},
        "end": {"type": "string"}
    },
    "required": ["id", "room", "user", "start", "end"]
}

# Схема ответа DELETE
DELETE_BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"}
    },
    "required": ["message"]
}

# Схема ошибки
ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string"}
    },
    "required": ["detail"]
}