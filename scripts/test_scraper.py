"""
Test scraping script for development
"""

import asyncio
import logging
from app.core.logging import setup_logging
from app.services.scraper import ScrapingService

setup_logging()
logger = logging.getLogger(__name__)


async def test_scraping():
    """Test the scraping functionality"""
    logger.info("Starting test scraping...")
    
    scraper = ScrapingService()
    
    try:
        # Test scraping for US region
        await scraper.scrape_region_deals("US")
        logger.info("Test scraping completed successfully")
        
    except Exception as e:
        logger.error(f"Test scraping failed: {e}")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_scraping())
