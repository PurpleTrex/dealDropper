"""
Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class ProductResponse(BaseModel):
    id: int
    asin: str
    title: str
    current_price: float
    original_price: Optional[float]
    discount_percentage: Optional[float]
    rating: Optional[float]
    review_count: Optional[int]
    image_url: Optional[str]
    affiliate_url: Optional[str]
    category: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DealResponse(BaseModel):
    id: int
    title: str
    current_price: float
    original_price: Optional[float]
    discount_percentage: float
    rating: Optional[float]
    image_url: Optional[str]
    affiliate_url: str
    category: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    max_price: Optional[float] = None
    min_discount: Optional[float] = None


class UserResponse(BaseModel):
    id: int
    email: str
    is_premium: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int = 0
    total_deals: int = 0
    total_users: int = 0
    products_today: int = 0
    deals_today: int = 0
    top_deals: List[dict] = []
    categories: List[dict] = []
    channels: dict = {}


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    min_discount: Optional[float] = None
    max_price: Optional[float] = None


class AnalyticsResponse(BaseModel):
    daily_deals: List[dict]
    avg_discount: float
    avg_price: float
    avg_rating: float
