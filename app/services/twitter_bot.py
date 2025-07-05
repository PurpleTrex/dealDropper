"""
Twitter bot service
"""

import logging
from typing import Optional
import tweepy

from app.core.config import settings

logger = logging.getLogger(__name__)


class TwitterBot:
    def __init__(self):
        self.api = None
        self.client = None
        
        if all([
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        ]):
            # v1.1 API for media upload
            auth = tweepy.OAuth1UserHandler(
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET,
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET
            )
            self.api = tweepy.API(auth)
            
            # v2 API for posting
            self.client = tweepy.Client(
                bearer_token=None,
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
            )
    
    async def send_deal(self, message: str, product) -> bool:
        """Send deal to Twitter"""
        if not self.client:
            logger.warning("Twitter client not configured")
            return False
            
        try:
            # Truncate message to fit Twitter limits
            tweet_text = self.format_tweet(message, product)
            
            # Post tweet
            response = self.client.create_tweet(text=tweet_text)
            
            if response.data:
                logger.info(f"Sent Twitter post for: {product.title}")
                return True
            else:
                logger.error("Failed to post tweet")
                return False
                
        except tweepy.TweepyException as e:
            logger.error(f"Twitter error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Twitter post: {e}")
            return False
    
    def format_tweet(self, message: str, product) -> str:
        """Format message for Twitter character limits"""
        max_length = 270  # Leave room for link
        
        # Create base tweet
        discount_emoji = "🔥" if product.discount_percentage > 30 else "💰"
        
        tweet = f"{discount_emoji} {product.title}\n"
        
        if product.discount_percentage > 0:
            tweet += f"🏷️ {product.discount_percentage}% OFF\n"
            
        tweet += f"💸 ${product.current_price:.2f}\n"
        
        if product.rating:
            stars = "⭐" * int(product.rating)
            tweet += f"{stars} {product.rating}/5\n"
        
        # Add hashtags
        hashtags = f"\n#AmazonDeals #Deals #{product.category or 'Shopping'}"
        
        # Add link
        link = f"\n{product.affiliate_url}"
        
        # Check length and truncate if necessary
        full_tweet = tweet + hashtags + link
        
        if len(full_tweet) > max_length:
            # Truncate title if needed
            available_length = max_length - len(hashtags) - len(link) - 50  # Buffer
            if len(tweet) > available_length:
                # Truncate title part
                title_limit = available_length - 50
                truncated_title = product.title[:title_limit] + "..."
                tweet = tweet.replace(product.title, truncated_title)
        
        return tweet + hashtags + link
    
    async def send_tweet(self, text: str) -> bool:
        """Send simple tweet"""
        if not self.client:
            return False
            
        try:
            response = self.client.create_tweet(text=text)
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error sending tweet: {e}")
            return False
