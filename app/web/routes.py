"""
Web routes for the frontend
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.services.analytics import AnalyticsService

web_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
analytics_service = AnalyticsService()


@web_router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    """Home page with latest deals"""
    
    # Get latest deals
    result = await db.execute("""
        SELECT p.*, d.* FROM products p
        JOIN deals d ON p.id = d.product_id
        WHERE p.discount_percentage >= 20
        ORDER BY d.created_at DESC
        LIMIT 20
    """)
    
    deals = result.fetchall()
    
    # Get trending products
    trending_result = await db.execute("""
        SELECT * FROM products
        WHERE is_trending = true
        AND rating >= 4.0
        ORDER BY rating DESC
        LIMIT 10
    """)
    
    trending = trending_result.fetchall()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "deals": deals,
        "trending": trending,
        "page_title": "DealDropper - Best Amazon Deals"
    })


@web_router.get("/deals", response_class=HTMLResponse)
async def deals_page(
    request: Request, 
    category: Optional[str] = None,
    page: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Deals listing page"""
    
    limit = 24
    offset = (page - 1) * limit
    
    query = """
        SELECT p.*, d.* FROM products p
        JOIN deals d ON p.id = d.product_id
        WHERE 1=1
    """
    params = {}
    
    if category:
        query += " AND p.category = :category"
        params["category"] = category
    
    query += " ORDER BY p.discount_percentage DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = await db.execute(query, params)
    deals = result.fetchall()
    
    # Get categories for filter
    categories_result = await db.execute(
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
    )
    categories = [row[0] for row in categories_result.fetchall()]
    
    return templates.TemplateResponse("deals.html", {
        "request": request,
        "deals": deals,
        "categories": categories,
        "current_category": category,
        "page": page,
        "page_title": f"Deals{' - ' + category if category else ''}"
    })


@web_router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    
    stats = await analytics_service.get_dashboard_stats()
    performance = await analytics_service.get_performance_metrics(30)
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "stats": stats,
        "performance": performance,
        "page_title": "Admin Dashboard"
    })


@web_router.post("/subscribe")
async def subscribe(
    request: Request,
    email: str = Form(...),
    categories: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to deal alerts"""
    try:
        # Check if user already exists
        existing = await db.execute(
            "SELECT * FROM users WHERE email = :email",
            {"email": email}
        )
        
        if existing.fetchone():
            return templates.TemplateResponse("subscribe.html", {
                "request": request,
                "error": "Email already subscribed",
                "page_title": "Subscribe"
            })
        
        # Create new user
        from app.core.database import User
        new_user = User(
            email=email,
            preferred_categories=categories
        )
        
        db.add(new_user)
        await db.commit()
        
        return templates.TemplateResponse("subscribe.html", {
            "request": request,
            "success": "Successfully subscribed to deal alerts!",
            "page_title": "Subscribe"
        })
        
    except Exception as e:
        return templates.TemplateResponse("subscribe.html", {
            "request": request,
            "error": "An error occurred. Please try again.",
            "page_title": "Subscribe"
        })


@web_router.get("/subscribe", response_class=HTMLResponse)
async def subscribe_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Subscribe page"""
    
    # Get categories
    result = await db.execute(
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
    )
    categories = [row[0] for row in result.fetchall()]
    
    return templates.TemplateResponse("subscribe.html", {
        "request": request,
        "categories": categories,
        "page_title": "Subscribe to Deal Alerts"
    })


@web_router.get("/search", response_class=HTMLResponse)
async def search_deals(
    request: Request,
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Search deals"""
    
    deals = []
    if q and len(q) >= 3:
        result = await db.execute("""
            SELECT p.*, d.* FROM products p
            JOIN deals d ON p.id = d.product_id
            WHERE p.title ILIKE :search_term
            ORDER BY p.discount_percentage DESC
            LIMIT 50
        """, {"search_term": f"%{q}%"})
        
        deals = result.fetchall()
    
    return templates.TemplateResponse("search.html", {
        "request": request,
        "deals": deals,
        "query": q,
        "page_title": f"Search Results{' for ' + q if q else ''}"
    })
