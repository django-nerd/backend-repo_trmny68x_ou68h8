"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class HoroscopeReading(BaseModel):
    """
    Horoscope readings collection
    Collection name: "horoscopereading"
    """
    sign: str = Field(..., description="Zodiac sign (aries, taurus, ...)")
    scope_date: date = Field(..., description="Date the horoscope applies to")
    headline: str = Field(..., description="Catchy one-liner for the reading")
    description: str = Field(..., description="Full horoscope text")
    mood: str = Field(..., description="Overall vibe")
    lucky_number: int = Field(..., ge=0, le=99, description="Lucky number for the day")
    lucky_color: str = Field(..., description="Lucky color suggestion")
    keywords: List[str] = Field(default_factory=list, description="Keyword tags for the reading")
    compatibility: Optional[str] = Field(None, description="Best compatible sign today")
