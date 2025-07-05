"""
Test script for the application
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal, Product, Deal, User
from app.services.affiliate import AffiliateService
from app.services.analytics import AnalyticsService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test database connection"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def test_affiliate_service():
    """Test affiliate service"""
    try:
        affiliate_service = AffiliateService()
        test_url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = await affiliate_service.create_affiliate_url(test_url)
        
        if "tag=" in affiliate_url:
            logger.info("✅ Affiliate service working")
            return True
        else:
            logger.error("❌ Affiliate service not adding tags")
            return False
    except Exception as e:
        logger.error(f"❌ Affiliate service failed: {e}")
        return False


async def test_analytics_service():
    """Test analytics service"""
    try:
        analytics_service = AnalyticsService()
        stats = await analytics_service.get_dashboard_stats()
        logger.info("✅ Analytics service working")
        return True
    except Exception as e:
        logger.error(f"❌ Analytics service failed: {e}")
        return False


async def create_sample_data():
    """Create sample data for testing"""
    try:
        async with AsyncSessionLocal() as session:
            # Create sample products
            sample_products = [
                {
                    "asin": "B08N5WRWNW",
                    "title": "Echo Dot (4th Gen) | Smart speaker with Alexa",
                    "current_price": 29.99,
                    "original_price": 49.99,
                    "discount_percentage": 40,
                    "rating": 4.5,
                    "review_count": 15000,
                    "category": "electronics",
                    "product_url": "https://www.amazon.com/dp/B08N5WRWNW",
                    "affiliate_url": "https://www.amazon.com/dp/B08N5WRWNW?tag=dealDropper-20",
                    "is_lightning_deal": True
                },
                {
                    "asin": "B07FZ8S74R",
                    "title": "Amazon Fire TV Stick 4K",
                    "current_price": 39.99,
                    "original_price": 49.99,
                    "discount_percentage": 20,
                    "rating": 4.3,
                    "review_count": 8500,
                    "category": "electronics",
                    "product_url": "https://www.amazon.com/dp/B07FZ8S74R",
                    "affiliate_url": "https://www.amazon.com/dp/B07FZ8S74R?tag=dealDropper-20",
                    "is_trending": True
                }
            ]
            
            for product_data in sample_products:
                # Check if product already exists
                existing = await session.execute(
                    "SELECT * FROM products WHERE asin = :asin",
                    {"asin": product_data["asin"]}
                )
                
                if not existing.fetchone():
                    product = Product(**product_data)
                    session.add(product)
            
            await session.commit()
            logger.info("✅ Sample data created")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    logger.info("🧪 Running application tests...")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Affiliate Service", test_affiliate_service),
        ("Analytics Service", test_analytics_service),
        ("Sample Data Creation", create_sample_data)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        results[test_name] = await test_func()
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    logger.info(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Application is ready to use.")
    else:
        logger.warning("⚠️  Some tests failed. Please check the configuration.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
