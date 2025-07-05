"""
API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db, Product, Deal, User
from app.services.analytics import AnalyticsService
from app.api.schemas import ProductResponse, DealResponse, UserCreate, DashboardStats

api_router = APIRouter()
analytics_service = AnalyticsService()


@api_router.get("/deals", response_model=List[DealResponse])
async def get_deals(
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    category: Optional[str] = None,
    min_discount: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent deals"""
    query = """
        SELECT p.*, d.* FROM products p
        JOIN deals d ON p.id = d.product_id
        WHERE 1=1
    """
    params = {}
    
    if category:
        query += " AND p.category = :category"
        params["category"] = category
    
    if min_discount:
        query += " AND p.discount_percentage >= :min_discount"
        params["min_discount"] = min_discount
    
    query += " ORDER BY d.created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = await db.execute(query, params)
    deals = result.fetchall()
    
    return [
        DealResponse(
            id=deal.id,
            title=deal.title,
            current_price=deal.current_price,
            original_price=deal.original_price,
            discount_percentage=deal.discount_percentage,
            rating=deal.rating,
            image_url=deal.image_url,
            affiliate_url=deal.affiliate_url,
            category=deal.category,
            created_at=deal.created_at
        )
        for deal in deals
    ]


@api_router.get("/products", response_model=List[ProductResponse])
async def get_products(
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get products"""
    query = "SELECT * FROM products WHERE 1=1"
    params = {}
    
    if category:
        query += " AND category = :category"
        params["category"] = category
    
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = await db.execute(query, params)
    products = result.fetchall()
    
    return [
        ProductResponse(
            id=product.id,
            asin=product.asin,
            title=product.title,
            current_price=product.current_price,
            original_price=product.original_price,
            discount_percentage=product.discount_percentage,
            rating=product.rating,
            review_count=product.review_count,
            image_url=product.image_url,
            affiliate_url=product.affiliate_url,
            category=product.category,
            created_at=product.created_at
        )
        for product in products
    ]


@api_router.post("/subscribe")
async def subscribe_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Subscribe user to deal alerts"""
    try:
        # Check if user already exists
        existing = await db.execute(
            "SELECT * FROM users WHERE email = :email",
            {"email": user.email}
        )
        
        if existing.fetchone():
            raise HTTPException(status_code=400, detail="Email already subscribed")
        
        # Create new user
        new_user = User(
            email=user.email,
            telegram_id=user.telegram_id,
            discord_id=user.discord_id,
            preferred_categories=",".join(user.preferred_categories) if user.preferred_categories else None,
            max_price=user.max_price,
            min_discount=user.min_discount
        )
        
        db.add(new_user)
        await db.commit()
        
        return {"message": "Successfully subscribed to deal alerts"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get available product categories"""
    result = await db.execute(
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
    )
    categories = [row[0] for row in result.fetchall()]
    return {"categories": categories}


@api_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = await analytics_service.get_dashboard_stats()
    return DashboardStats(**stats)


@api_router.get("/search")
async def search_deals(
    q: str = Query(..., min_length=3),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Search deals by keyword"""
    query = """
        SELECT p.*, d.* FROM products p
        JOIN deals d ON p.id = d.product_id
        WHERE p.title ILIKE :search_term
        ORDER BY p.discount_percentage DESC
        LIMIT :limit
    """
    
    result = await db.execute(query, {
        "search_term": f"%{q}%",
        "limit": limit
    })
    
    deals = result.fetchall()
    
    return [
        {
            "id": deal.id,
            "title": deal.title,
            "current_price": deal.current_price,
            "discount_percentage": deal.discount_percentage,
            "rating": deal.rating,
            "image_url": deal.image_url,
            "affiliate_url": deal.affiliate_url
        }
        for deal in deals
    ]


@api_router.get("/trending")
async def get_trending_deals(
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get trending deals (best sellers)"""
    query = """
        SELECT * FROM products
        WHERE is_trending = true
        AND rating >= :min_rating
        ORDER BY rating DESC, review_count DESC
        LIMIT :limit
    """
    
    result = await db.execute(query, {
        "min_rating": 4.0,
        "limit": limit
    })
    
    products = result.fetchall()
    
    return [
        {
            "id": product.id,
            "title": product.title,
            "current_price": product.current_price,
            "rating": product.rating,
            "review_count": product.review_count,
            "image_url": product.image_url,
            "affiliate_url": product.affiliate_url,
            "category": product.category
        }
        for product in products
    ]
