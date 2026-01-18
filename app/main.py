from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
import gridfs
import io
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "event_management_db")

app = FastAPI(title="Event Management API")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Sync client ONLY for GridFS (file storage)
sync_client = MongoClient(MONGO_URI)
sync_db = sync_client[DB_NAME]
fs = gridfs.GridFS(sync_db)

# ----------------------------
#  HEALTH CHECK ENDPOINTS
# ----------------------------

@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health/db")
async def health_db():
    # Simple ping to confirm Atlas connection
    await db.command("ping")
    return {"status": "ok", "db": DB_NAME}

# ----------------------------
#  VENUE ENDPOINTS
# ----------------------------

class VenueIn(BaseModel):
    name: str = Field(..., min_length=2)
    address: str = Field(..., min_length=3)
    capacity: int = Field(..., ge=1)

class VenueOut(VenueIn):
    id: str

def venue_out(doc) -> VenueOut:
    return VenueOut(
        id=str(doc["_id"]),
        name=doc["name"],
        address=doc["address"],
        capacity=doc["capacity"],
    )

@app.post("/venues", response_model=VenueOut)
async def create_venue(venue: VenueIn):
    result = await db.venues.insert_one(venue.model_dump())
    doc = await db.venues.find_one({"_id": result.inserted_id})
    return venue_out(doc)

@app.get("/venues", response_model=List[VenueOut])
async def list_venues():
    venues = []
    async for doc in db.venues.find():
        venues.append(venue_out(doc))
    return venues

@app.get("/venues/{venue_id}", response_model=VenueOut)
async def get_venue(venue_id: str):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    doc = await db.venues.find_one({"_id": ObjectId(venue_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Venue not found")

    return venue_out(doc)

@app.put("/venues/{venue_id}", response_model=VenueOut)
async def update_venue(venue_id: str, venue: VenueIn):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    result = await db.venues.update_one(
        {"_id": ObjectId(venue_id)},
        {"$set": venue.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")

    doc = await db.venues.find_one({"_id": ObjectId(venue_id)})
    return venue_out(doc)

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    result = await db.venues.delete_one({"_id": ObjectId(venue_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")

    return {"message": "Venue deleted"}

# ----------------------------
#  EVENTS (CRUD)
# ----------------------------

class EventIn(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    venue_id: str = Field(..., min_length=24)  # ObjectId as string
    date: str = Field(..., min_length=4)  # keep simple (ISO string recommended)
    max_attendees: int = Field(..., ge=1)

class EventOut(EventIn):
    id: str
    poster_file_id: Optional[str] = None
    promo_video_file_id: Optional[str] = None

def event_out(doc) -> EventOut:
    return EventOut(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        venue_id=doc["venue_id"],
        date=doc["date"],
        max_attendees=doc["max_attendees"],
        poster_file_id=doc.get("poster_file_id"),
        promo_video_file_id=doc.get("promo_video_file_id"),
    )

@app.post("/events", response_model=EventOut)
async def create_event(event: EventIn):
    # validate venue_id
    if not ObjectId.is_valid(event.venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    # optional: ensure venue exists
    venue = await db.venues.find_one({"_id": ObjectId(event.venue_id)})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    result = await db.events.insert_one(event.model_dump())
    doc = await db.events.find_one({"_id": result.inserted_id})
    return event_out(doc)

@app.get("/events", response_model=List[EventOut])
async def list_events():
    events = []
    async for doc in db.events.find():
        events.append(event_out(doc))
    return events

@app.get("/events/{event_id}", response_model=EventOut)
async def get_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    doc = await db.events.find_one({"_id": ObjectId(event_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Event not found")

    return event_out(doc)

@app.put("/events/{event_id}", response_model=EventOut)
async def update_event(event_id: str, event: EventIn):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    if not ObjectId.is_valid(event.venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    venue = await db.venues.find_one({"_id": ObjectId(event.venue_id)})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    result = await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": event.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    doc = await db.events.find_one({"_id": ObjectId(event_id)})
    return event_out(doc)

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event deleted"}

# ----------------------------
#  BOOKINGS (CRUD)
# ----------------------------

class BookingIn(BaseModel):
    event_id: str = Field(..., min_length=24)     # ObjectId str
    attendee_id: str = Field(..., min_length=24)  # ObjectId str
    tickets: int = Field(..., ge=1)
    booking_date: str = Field(..., min_length=4)  # ISO string recommended

class BookingOut(BookingIn):
    id: str

def booking_out(doc) -> BookingOut:
    return BookingOut(
        id=str(doc["_id"]),
        event_id=doc["event_id"],
        attendee_id=doc["attendee_id"],
        tickets=doc["tickets"],
        booking_date=doc["booking_date"],
    )

@app.post("/bookings", response_model=BookingOut)
async def create_booking(booking: BookingIn):
    # validate ids
    if not ObjectId.is_valid(booking.event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")
    if not ObjectId.is_valid(booking.attendee_id):
        raise HTTPException(status_code=400, detail="Invalid attendee id")

    # ensure event exists
    event = await db.events.find_one({"_id": ObjectId(booking.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # ensure attendee exists
    attendee = await db.attendees.find_one({"_id": ObjectId(booking.attendee_id)})
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    result = await db.bookings.insert_one(booking.model_dump())
    doc = await db.bookings.find_one({"_id": result.inserted_id})
    return booking_out(doc)

@app.get("/bookings", response_model=List[BookingOut])
async def list_bookings():
    bookings = []
    async for doc in db.bookings.find():
        bookings.append(booking_out(doc))
    return bookings

@app.get("/bookings/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: str):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking id")

    doc = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking_out(doc)

@app.put("/bookings/{booking_id}", response_model=BookingOut)
async def update_booking(booking_id: str, booking: BookingIn):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking id")

    if not ObjectId.is_valid(booking.event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")
    if not ObjectId.is_valid(booking.attendee_id):
        raise HTTPException(status_code=400, detail="Invalid attendee id")

    event = await db.events.find_one({"_id": ObjectId(booking.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    attendee = await db.attendees.find_one({"_id": ObjectId(booking.attendee_id)})
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    result = await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": booking.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    doc = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    return booking_out(doc)

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking id")

    result = await db.bookings.delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"message": "Booking deleted"}


# ----------------------------
#  ATTENDEES (CRUD)
# ----------------------------

class AttendeeIn(BaseModel):
    name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    phone: Optional[str] = None

class AttendeeOut(AttendeeIn):
    id: str

def attendee_out(doc) -> AttendeeOut:
    return AttendeeOut(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
        phone=doc.get("phone"),
    )

@app.post("/attendees", response_model=AttendeeOut)
async def create_attendee(attendee: AttendeeIn):
    result = await db.attendees.insert_one(attendee.model_dump())
    doc = await db.attendees.find_one({"_id": result.inserted_id})
    return attendee_out(doc)

@app.get("/attendees", response_model=List[AttendeeOut])
async def list_attendees():
    attendees = []
    async for doc in db.attendees.find():
        attendees.append(attendee_out(doc))
    return attendees

@app.get("/attendees/{attendee_id}", response_model=AttendeeOut)
async def get_attendee(attendee_id: str):
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid attendee id")

    doc = await db.attendees.find_one({"_id": ObjectId(attendee_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Attendee not found")

    return attendee_out(doc)

@app.put("/attendees/{attendee_id}", response_model=AttendeeOut)
async def update_attendee(attendee_id: str, attendee: AttendeeIn):
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid attendee id")

    result = await db.attendees.update_one(
        {"_id": ObjectId(attendee_id)},
        {"$set": attendee.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")

    doc = await db.attendees.find_one({"_id": ObjectId(attendee_id)})
    return attendee_out(doc)

@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid attendee id")

    result = await db.attendees.delete_one({"_id": ObjectId(attendee_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")

    return {"message": "Attendee deleted"}



# ----------------------------
#  MEDIA (GridFS) ENDPOINTS
# ----------------------------

@app.post("/venues/{venue_id}/photo")
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        contentType=file.content_type,
        meta={"type": "venue_photo", "venue_id": venue_id}
    )

    await db.venues.update_one(
        {"_id": ObjectId(venue_id)},
        {"$set": {"photo_file_id": str(file_id)}}
    )

    return {"message": "Venue photo uploaded", "file_id": str(file_id)}


@app.get("/venues/{venue_id}/photo")
async def get_venue_photo(venue_id: str):
    if not ObjectId.is_valid(venue_id):
        raise HTTPException(status_code=400, detail="Invalid venue id")

    venue = await db.venues.find_one({"_id": ObjectId(venue_id)})
    if not venue or "photo_file_id" not in venue:
        raise HTTPException(status_code=404, detail="Venue photo not found")

    file_id = venue["photo_file_id"]
    grid_out = fs.get(ObjectId(file_id))

    return StreamingResponse(
        io.BytesIO(grid_out.read()),
        media_type=grid_out.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{grid_out.filename}"'}
    )


@app.post("/events/{event_id}/poster")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        contentType=file.content_type,
        meta={"type": "event_poster", "event_id": event_id}
    )

    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"poster_file_id": str(file_id)}}
    )

    return {"message": "Event poster uploaded", "file_id": str(file_id)}


@app.get("/events/{event_id}/poster")
async def get_event_poster(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event or "poster_file_id" not in event:
        raise HTTPException(status_code=404, detail="Event poster not found")

    file_id = event["poster_file_id"]
    grid_out = fs.get(ObjectId(file_id))

    return StreamingResponse(
        io.BytesIO(grid_out.read()),
        media_type=grid_out.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{grid_out.filename}"'}
    )


@app.post("/events/{event_id}/promo-video")
async def upload_event_video(event_id: str, file: UploadFile = File(...)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        contentType=file.content_type,
        meta={"type": "promo_video", "event_id": event_id}
    )

    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"promo_video_file_id": str(file_id)}}
    )

    return {"message": "Promo video uploaded", "file_id": str(file_id)}


@app.get("/events/{event_id}/promo-video")
async def get_event_video(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event or "promo_video_file_id" not in event:
        raise HTTPException(status_code=404, detail="Promo video not found")

    file_id = event["promo_video_file_id"]
    grid_out = fs.get(ObjectId(file_id))

    return StreamingResponse(
        io.BytesIO(grid_out.read()),
        media_type=grid_out.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{grid_out.filename}"'}
    )


