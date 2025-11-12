import os
from datetime import date, datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import HoroscopeReading

app = FastAPI(title="Futuristic Horoscope API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    sign: str
    scope_date: Optional[date] = None


ZODIAC_SIGNS = {
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
}


@app.get("/")
def read_root():
    return {"message": "Futuristic Horoscope Backend is live"}


@app.get("/api/horoscope")
def get_horoscope(sign: str = Query(..., description="Zodiac sign"), scope_date: Optional[date] = None):
    """Fetch stored horoscope(s) for a sign and optional date."""
    if sign.lower() not in ZODIAC_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid zodiac sign")

    filt = {"sign": sign.lower()}
    if scope_date:
        # Pydantic stores date as datetime/date; our helper returns raw dicts
        filt["scope_date"] = scope_date

    docs = get_documents("horoscopereading", filt, limit=10)
    # Convert ObjectId and dates to string-safe outputs
    def normalize(doc):
        d = dict(doc)
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        if isinstance(d.get("scope_date"), (datetime, date)):
            d["scope_date"] = str(d["scope_date"])[:10]
        return d

    return {"results": [normalize(x) for x in docs]}


@app.post("/api/horoscope/generate")
def generate_and_store(req: GenerateRequest):
    """
    Generate a fresh horoscope-like reading (rule-based pseudo generation)
    and store it in the database for persistence.
    """
    sign = req.sign.lower()
    if sign not in ZODIAC_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid zodiac sign")

    d = req.scope_date or date.today()

    # Simple deterministic pseudo-generation based on sign + date hash
    seed = sum(ord(c) for c in (sign + d.isoformat()))
    moods = [
        "radiant", "introspective", "bold", "curious", "grounded", "electric",
        "serene", "magnetic", "fearless", "visionary", "playful", "resolute"
    ]
    colors = [
        "iridescent violet", "neon cyan", "plasma pink", "midnight indigo",
        "quantum gold", "holographic silver", "aurora teal", "cosmic amber"
    ]
    headlines = [
        "Orbit your potential.", "Align with the signal.", "Rewrite today’s script.",
        "Touch the ribbon of fate.", "Navigate the unknown.", "Spark a new circuit."
    ]
    keywords_pool = [
        "sync", "flow", "impulse", "clarity", "bridge", "pulse", "echo", "vector",
        "harmony", "signal", "orbit", "ribbon", "thrive", "link", "spark"
    ]
    compats = list(ZODIAC_SIGNS)

    mood = moods[seed % len(moods)]
    color = colors[seed % len(colors)]
    headline = headlines[seed % len(headlines)]
    lucky_number = (seed % 99) + 1
    compatibility = compats[seed % len(compats)]
    # Ensure compatibility not equal to the sign for variety
    if compatibility == sign:
        compatibility = compats[(seed + 3) % len(compats)]

    description = (
        f"Today, {sign.title()} tunes into a {mood} frequency."
        f" Signals you’ve been waiting on begin to resolve, forming patterns in plain sight."
        f" Trust your calibration and take one deliberate step forward."
        f" A chance encounter amplifies your intention—listen for echoes."
    )

    reading = HoroscopeReading(
        sign=sign,
        scope_date=d,
        headline=headline,
        description=description,
        mood=mood,
        lucky_number=lucky_number,
        lucky_color=color,
        keywords=[keywords_pool[(seed + i) % len(keywords_pool)] for i in range(3)],
        compatibility=compatibility,
    )

    inserted_id = create_document("horoscopereading", reading)

    return {
        "id": inserted_id,
        "reading": reading.model_dump()
    }


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
