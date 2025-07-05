"""
Distribution service for posting deals to various channels
"""

import asyncio
import logging
from typing import List
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Product, Deal
from app.services.telegram_bot import TelegramBot
from app.services.discord_bot import DiscordBot
from app.services.twitter_bot import TwitterBot
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class DistributionService:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.discord_bot = DiscordBot()
        self.twitter_bot = TwitterBot()
        self.email_service = EmailService()
    
    async def distribute_pending_deals(self):
        """Distribute deals that haven't been posted yet"""
        logger.info("Starting deal distribution...")
        
        try:
            async with AsyncSessionLocal() as session:
                # Get unposted deals from the last hour
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                
                # Query for products with good deals that haven't been posted
                query = """
                    SELECT p.* FROM products p
                    WHERE p.discount_percentage >= :min_discount
                    AND p.rating >= :min_rating
                    AND p.current_price <= :max_price
                    AND p.is_posted = false
                    AND p.created_at >= :cutoff_time
                    ORDER BY p.discount_percentage DESC
                    LIMIT 50
                """
                
                result = await session.execute(query, {
                    'min_discount': settings.MIN_DISCOUNT_PERCENTAGE,
                    'min_rating': settings.MIN_PRODUCT_RATING,
                    'max_price': settings.MAX_PRICE_USD,
                    'cutoff_time': cutoff_time
                })
                
                products = result.fetchall()
                
                for product in products:
                    await self.distribute_deal(product)
                    await asyncio.sleep(2)  # Rate limiting
                    
        except Exception as e:
            logger.error(f"Error in deal distribution: {e}")
        
        logger.info("Deal distribution completed")
    
    async def distribute_deal(self, product):
        """Distribute a single deal to all channels"""
        try:
            # Create deal message
            message = self.format_deal_message(product)
            
            # Post to channels
            tasks = [
                self.telegram_bot.send_deal(message, product),
                self.discord_bot.send_deal(message, product),
                self.twitter_bot.send_deal(message, product),
                self.email_service.queue_deal(product)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Track which channels succeeded
            posted_telegram = not isinstance(results[0], Exception)
            posted_discord = not isinstance(results[1], Exception)
            posted_twitter = not isinstance(results[2], Exception)
            posted_email = not isinstance(results[3], Exception)
            
            # Update database
            async with AsyncSessionLocal() as session:
                # Mark product as posted
                product_obj = await session.get(Product, product.id)
                if product_obj:
                    product_obj.is_posted = True
                
                # Create deal record
                deal = Deal(
                    product_id=product.id,
                    deal_type="discount" if product.discount_percentage > 0 else "trending",
                    discount_percentage=product.discount_percentage,
                    old_price=product.original_price,
                    new_price=product.current_price,
                    posted_telegram=posted_telegram,
                    posted_discord=posted_discord,
                    posted_twitter=posted_twitter,
                    posted_email=posted_email
                )
                session.add(deal)
                
                await session.commit()
                
            logger.info(f"Distributed deal: {product.title}")
            
        except Exception as e:
            logger.error(f"Error distributing deal {product.title}: {e}")
    
    def format_deal_message(self, product) -> str:
        """Format deal message for posting"""
        discount_text = ""
        if product.discount_percentage > 0:
            discount_text = f"🔥 {product.discount_percentage}% OFF! "
            
        price_text = f"${product.current_price:.2f}"
        if product.original_price and product.original_price != product.current_price:
            price_text += f" (was ${product.original_price:.2f})"
        
        rating_text = ""
        if product.rating:
            stars = "⭐" * int(product.rating)
            rating_text = f"\n{stars} {product.rating}/5"
            
        message = f"""
{discount_text}{product.title}

💰 {price_text}{rating_text}

🛒 Get it now: {product.affiliate_url}

#deals #amazon #{product.category or 'shopping'}
        """.strip()
        
        return message
    
    async def send_daily_newsletter(self):
        """Send daily newsletter with top deals"""
        try:
            # Get top deals from the last 24 hours
            async with AsyncSessionLocal() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                query = """
                    SELECT p.* FROM products p
                    WHERE p.created_at >= :cutoff_time
                    AND p.discount_percentage >= :min_discount
                    ORDER BY p.discount_percentage DESC
                    LIMIT 20
                """
                
                result = await session.execute(query, {
                    'cutoff_time': cutoff_time,
                    'min_discount': settings.MIN_DISCOUNT_PERCENTAGE
                })
                
                products = result.fetchall()
                
                if products:
                    await self.email_service.send_newsletter(products)
                    
        except Exception as e:
            logger.error(f"Error sending daily newsletter: {e}")
