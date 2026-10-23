from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
import os
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CRUD Bookit")

class BookingCreate(BaseModel):
    room_id: int
    user_name: str
    start_time: str
    end_time: str

class BookingUpdate(BaseModel):
    room_id: int
    user_name: str
    start_time: str
    end_time: str

class BookingPatch(BaseModel):
    room_id: Optional[int] = None
    user_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

def get_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.on_event("startup")
def init_db():
    time.sleep(3)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,  
                    room_id INT NOT NULL,
                    user_name VARCHAR(50) NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    UNIQUE(room_id, start_time)                
                )''')
    conn.commit()
    cur.close()
    conn.close()

@app.post("/bookings")
def create_booking(booking: BookingCreate):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO bookings (room_id, user_name, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING id",
                    (booking.room_id, booking.user_name, booking.start_time, booking.end_time))
        booking_id = cur.fetchone()[0]
        conn.commit()
        return {"id": booking_id, "status": "confirmed"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Room is already booked for this time")
    finally:
        cur.close()
        conn.close()

@app.get("/bookings/{room_id}")
def get_booking(room_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings WHERE room_id=%s", (room_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")
    return [{"id": r[0], "room": r[1], "user": r[2], "start": str(r[3]), "end": str(r[4])} for r in rows]

@app.put("/bookings/{booking_id}")
def update_booking(booking_id: int, booking: BookingUpdate):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM bookings WHERE id = %s", (booking_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Booking not found")
        cur.execute(
            """UPDATE bookings 
               SET room_id = %s, user_name = %s, start_time = %s, end_time = %s 
               WHERE id = %s 
               RETURNING id, room_id, user_name, start_time, end_time""",
            (booking.room_id, booking.user_name, booking.start_time, booking.end_time, booking_id)
        )
        row = cur.fetchone()
        conn.commit()
        return {"id": row[0], "room": row[1], "user": row[2], "start": str(row[3]), "end": str(row[4])}
    except HTTPException:
        raise
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Room is already booked for this time")
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.patch("/bookings/{booking_id}")
def update_booking_patch(booking_id: int, booking: BookingPatch):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        existing = cur.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        new_room = booking.room_id if booking.room_id is not None else existing[1]
        new_user = booking.user_name if booking.user_name is not None else existing[2]
        new_start = booking.start_time if booking.start_time is not None else str(existing[3])
        new_end = booking.end_time if booking.end_time is not None else str(existing[4])
        
        cur.execute(
            """UPDATE bookings 
               SET room_id = %s, user_name = %s, start_time = %s, end_time = %s 
               WHERE id = %s 
               RETURNING id, room_id, user_name, start_time, end_time""", 
            (new_room, new_user, new_start, new_end, booking_id)
        )
        row = cur.fetchone()
        conn.commit()
        return {"id": row[0], "room": row[1], "user": row[2], "start": str(row[3]), "end": str(row[4])}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Room is already booked for this time")
    finally:
        cur.close()
        conn.close()

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM bookings WHERE id = %s", (booking_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Booking not found")
        cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        conn.commit()
        return {"message": f"Booking {booking_id} deleted successfully"}
    finally:
        cur.close()
        conn.close()