from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "event_management_db")

app = FastAPI(title="Event Management API")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

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



@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health/db")
async def health_db():
    # Simple ping to confirm Atlas connection
    await db.command("ping")
    return {"status": "ok", "db": DB_NAME}

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

