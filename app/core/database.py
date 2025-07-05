"""
Database configuration and models
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, func
from datetime import datetime
import redis.asyncio as redis

from app.core.config import settings


# Database engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asin: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    product_url: Mapped[str] = mapped_column(Text)
    affiliate_url: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Pricing
    current_price: Mapped[float] = mapped_column(Float)
    original_price: Mapped[float] = mapped_column(Float, nullable=True)
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Reviews and ratings
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Metadata
    region: Mapped[str] = mapped_column(String(2), default="US")
    is_lightning_deal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False)
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    scraped_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telegram_id: Mapped[str] = mapped_column(String(50), nullable=True)
    discord_id: Mapped[str] = mapped_column(String(50), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Preferences
    preferred_categories: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    max_price: Mapped[float] = mapped_column(Float, nullable=True)
    min_discount: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Deal(Base):
    __tablename__ = "deals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    deal_type: Mapped[str] = mapped_column(String(50))  # lightning, discount, trending
    discount_percentage: Mapped[float] = mapped_column(Float)
    old_price: Mapped[float] = mapped_column(Float)
    new_price: Mapped[float] = mapped_column(Float)
    
    # Distribution tracking
    posted_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_discord: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_twitter: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_email: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Analytics(Base):
    __tablename__ = "analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(100))
    metric_value: Mapped[float] = mapped_column(Float)
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# Database session dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
