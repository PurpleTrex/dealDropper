"""
Analytics service for tracking metrics and performance
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Analytics, Product, Deal, User

logger = logging.getLogger(__name__)


class AnalyticsService:
    
    async def collect_daily_metrics(self):
        """Collect daily analytics metrics"""
        logger.info("Collecting daily analytics...")
        
        try:
            today = datetime.utcnow().date()
            metrics = {}
            
            async with AsyncSessionLocal() as session:
                # Products scraped today
                products_today = await session.execute(
                    "SELECT COUNT(*) FROM products WHERE DATE(created_at) = :today",
                    {"today": today}
                )
                metrics["products_scraped"] = products_today.scalar()
                
                # Deals posted today
                deals_today = await session.execute(
                    "SELECT COUNT(*) FROM deals WHERE DATE(created_at) = :today",
                    {"today": today}
                )
                metrics["deals_posted"] = deals_today.scalar()
                
                # Average discount percentage
                avg_discount = await session.execute(
                    "SELECT AVG(discount_percentage) FROM products WHERE DATE(created_at) = :today AND discount_percentage > 0",
                    {"today": today}
                )
                metrics["avg_discount"] = avg_discount.scalar() or 0
                
                # Channel distribution stats
                telegram_posts = await session.execute(
                    "SELECT COUNT(*) FROM deals WHERE DATE(created_at) = :today AND posted_telegram = true",
                    {"today": today}
                )
                metrics["telegram_posts"] = telegram_posts.scalar()
                
                discord_posts = await session.execute(
                    "SELECT COUNT(*) FROM deals WHERE DATE(created_at) = :today AND posted_discord = true",
                    {"today": today}
                )
                metrics["discord_posts"] = discord_posts.scalar()
                
                twitter_posts = await session.execute(
                    "SELECT COUNT(*) FROM deals WHERE DATE(created_at) = :today AND posted_twitter = true",
                    {"today": today}
                )
                metrics["twitter_posts"] = twitter_posts.scalar()
                
                # User growth
                new_users = await session.execute(
                    "SELECT COUNT(*) FROM users WHERE DATE(created_at) = :today",
                    {"today": today}
                )
                metrics["new_users"] = new_users.scalar()
                
                # Save metrics
                for metric_name, value in metrics.items():
                    analytic = Analytics(
                        metric_name=metric_name,
                        metric_value=float(value),
                        date=datetime.utcnow()
                    )
                    session.add(analytic)
                
                await session.commit()
                
            logger.info(f"Collected {len(metrics)} metrics for {today}")
            
        except Exception as e:
            logger.error(f"Error collecting analytics: {e}")
    
    async def get_dashboard_stats(self) -> Dict:
        """Get stats for admin dashboard"""
        try:
            async with AsyncSessionLocal() as session:
                stats = {}
                
                # Total counts
                total_products = await session.execute("SELECT COUNT(*) FROM products")
                stats["total_products"] = total_products.scalar()
                
                total_deals = await session.execute("SELECT COUNT(*) FROM deals")
                stats["total_deals"] = total_deals.scalar()
                
                total_users = await session.execute("SELECT COUNT(*) FROM users")
                stats["total_users"] = total_users.scalar()
                
                # Today's activity
                today = datetime.utcnow().date()
                
                products_today = await session.execute(
                    "SELECT COUNT(*) FROM products WHERE DATE(created_at) = :today",
                    {"today": today}
                )
                stats["products_today"] = products_today.scalar()
                
                deals_today = await session.execute(
                    "SELECT COUNT(*) FROM deals WHERE DATE(created_at) = :today",
                    {"today": today}
                )
                stats["deals_today"] = deals_today.scalar()
                
                # Best performing deals (last 7 days)
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                top_deals = await session.execute("""
                    SELECT p.title, p.discount_percentage, p.current_price, p.affiliate_url
                    FROM products p
                    JOIN deals d ON p.id = d.product_id
                    WHERE p.created_at >= :week_ago
                    ORDER BY p.discount_percentage DESC
                    LIMIT 10
                """, {"week_ago": week_ago})
                
                stats["top_deals"] = [
                    {
                        "title": row[0],
                        "discount": row[1],
                        "price": row[2],
                        "url": row[3]
                    }
                    for row in top_deals.fetchall()
                ]
                
                # Category breakdown
                category_stats = await session.execute("""
                    SELECT category, COUNT(*) as count
                    FROM products
                    WHERE created_at >= :week_ago
                    GROUP BY category
                    ORDER BY count DESC
                    LIMIT 10
                """, {"week_ago": week_ago})
                
                stats["categories"] = [
                    {"category": row[0] or "Unknown", "count": row[1]}
                    for row in category_stats.fetchall()
                ]
                
                # Channel performance
                channel_stats = await session.execute("""
                    SELECT 
                        SUM(CASE WHEN posted_telegram THEN 1 ELSE 0 END) as telegram,
                        SUM(CASE WHEN posted_discord THEN 1 ELSE 0 END) as discord,
                        SUM(CASE WHEN posted_twitter THEN 1 ELSE 0 END) as twitter,
                        SUM(CASE WHEN posted_email THEN 1 ELSE 0 END) as email
                    FROM deals
                    WHERE created_at >= :week_ago
                """, {"week_ago": week_ago})
                
                channel_row = channel_stats.fetchone()
                stats["channels"] = {
                    "telegram": channel_row[0] or 0,
                    "discord": channel_row[1] or 0,
                    "twitter": channel_row[2] or 0,
                    "email": channel_row[3] or 0
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    async def get_performance_metrics(self, days: int = 30) -> Dict:
        """Get performance metrics for specified period"""
        try:
            async with AsyncSessionLocal() as session:
                start_date = datetime.utcnow() - timedelta(days=days)
                
                # Daily deal counts
                daily_deals = await session.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM deals
                    WHERE created_at >= :start_date
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """, {"start_date": start_date})
                
                daily_data = [
                    {"date": row[0].isoformat(), "deals": row[1]}
                    for row in daily_deals.fetchall()
                ]
                
                # Average metrics
                avg_metrics = await session.execute("""
                    SELECT 
                        AVG(discount_percentage) as avg_discount,
                        AVG(current_price) as avg_price,
                        AVG(rating) as avg_rating
                    FROM products p
                    JOIN deals d ON p.id = d.product_id
                    WHERE d.created_at >= :start_date
                """, {"start_date": start_date})
                
                avg_row = avg_metrics.fetchone()
                
                return {
                    "daily_deals": daily_data,
                    "avg_discount": round(avg_row[0] or 0, 2),
                    "avg_price": round(avg_row[1] or 0, 2),
                    "avg_rating": round(avg_row[2] or 0, 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def track_affiliate_revenue(self, product_id: int, revenue: float):
        """Track affiliate revenue (placeholder for future implementation)"""
        try:
            async with AsyncSessionLocal() as session:
                analytic = Analytics(
                    metric_name="affiliate_revenue",
                    metric_value=revenue,
                    date=datetime.utcnow()
                )
                session.add(analytic)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
