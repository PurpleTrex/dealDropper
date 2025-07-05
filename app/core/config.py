"""
Application configuration settings
"""

import os
from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "DealDropper"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "change-this-secret-key-in-production"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/dealDropper"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Amazon Configuration
    AMAZON_ASSOCIATES_ID: str = ""
    AMAZON_REGIONS: str = "US,UK,CA"
    
    # Social Media APIs
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_CHANNEL_ID: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    
    # Email Configuration
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "deals@yourdomain.com"
    
    # Link Shortening
    BITLY_ACCESS_TOKEN: str = ""
    
    # Admin Configuration
    ADMIN_EMAIL: str = "admin@yourdomain.com"
    ADMIN_PASSWORD: str = "change-this-password"
    
    # Scraping Configuration
    USER_AGENTS_ROTATE: bool = True
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_DELAY_MIN: int = 1
    REQUEST_DELAY_MAX: int = 3
    USE_PROXY: bool = False
    PROXY_LIST: str = ""
    
    # Deal Filtering
    MIN_DISCOUNT_PERCENTAGE: int = 20
    MIN_PRODUCT_RATING: float = 4.0
    MIN_REVIEW_COUNT: int = 50
    MAX_PRICE_USD: float = 500.0
    
    # Scheduler Settings
    SCRAPING_INTERVAL_MINUTES: int = 15
    POSTING_INTERVAL_MINUTES: int = 5
    CLEANUP_INTERVAL_HOURS: int = 24
    
    @property
    def amazon_regions_list(self) -> List[str]:
        return [region.strip() for region in self.AMAZON_REGIONS.split(",")]
    
    @property
    def proxy_list(self) -> List[str]:
        if not self.PROXY_LIST:
            return []
        return [proxy.strip() for proxy in self.PROXY_LIST.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
