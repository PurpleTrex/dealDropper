"""
Task scheduler for automated operations
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = AsyncIOScheduler()


def setup_jobs():
    """Setup scheduled jobs"""
    
    # Import here to avoid circular imports
    from app.services.scraper import ScrapingService
    from app.services.distributor import DistributionService
    from app.services.analytics import AnalyticsService
    
    scraper = ScrapingService()
    distributor = DistributionService()
    analytics = AnalyticsService()
    
    # Scraping job
    scheduler.add_job(
        scraper.scrape_deals,
        trigger=IntervalTrigger(minutes=settings.SCRAPING_INTERVAL_MINUTES),
        id="scrape_deals",
        name="Scrape Amazon deals",
        replace_existing=True
    )
    
    # Distribution job
    scheduler.add_job(
        distributor.distribute_pending_deals,
        trigger=IntervalTrigger(minutes=settings.POSTING_INTERVAL_MINUTES),
        id="distribute_deals",
        name="Distribute deals to channels",
        replace_existing=True
    )
    
    # Analytics job
    scheduler.add_job(
        analytics.collect_daily_metrics,
        trigger=IntervalTrigger(hours=settings.CLEANUP_INTERVAL_HOURS),
        id="collect_analytics",
        name="Collect analytics metrics",
        replace_existing=True
    )
    
    logger.info("Scheduled jobs configured")


# Setup jobs when module is imported
setup_jobs()
