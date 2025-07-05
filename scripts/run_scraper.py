"""
Manual scraping script for testing
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper import ScrapingService
from app.services.distributor import DistributionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_scraper():
    """Run scraper manually"""
    logger.info("Starting manual scraping...")
    
    scraper = ScrapingService()
    
    try:
        await scraper.scrape_deals()
        logger.info("Scraping completed successfully")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
    finally:
        await scraper.close()


async def run_distributor():
    """Run distributor manually"""
    logger.info("Starting manual distribution...")
    
    distributor = DistributionService()
    
    try:
        await distributor.distribute_pending_deals()
        logger.info("Distribution completed successfully")
    except Exception as e:
        logger.error(f"Distribution failed: {e}")


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python run_scraper.py [scrape|distribute|both]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "scrape":
        await run_scraper()
    elif action == "distribute":
        await run_distributor()
    elif action == "both":
        await run_scraper()
        await run_distributor()
    else:
        print("Invalid action. Use: scrape, distribute, or both")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
