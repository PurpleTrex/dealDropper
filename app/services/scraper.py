"""
Amazon scraping service
"""

import asyncio
import logging
import random
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Product, Deal
from app.services.affiliate import AffiliateService

logger = logging.getLogger(__name__)

try:
    import aiohttp
    from bs4 import BeautifulSoup
    from fake_useragent import UserAgent
    SCRAPING_DEPS_AVAILABLE = True
except ImportError:
    SCRAPING_DEPS_AVAILABLE = False
    logger.warning("Scraping dependencies not available. Install beautifulsoup4, aiohttp, fake-useragent")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium dependencies not available. Install selenium, undetected-chromedriver")


class ScrapingService:
    def __init__(self):
        if not SCRAPING_DEPS_AVAILABLE:
            logger.error("Scraping dependencies not available. Service will be disabled.")
            return
            
        self.ua = UserAgent()
        self.affiliate_service = AffiliateService()
        self.session = None
        
    async def get_session(self):
        """Get aiohttp session"""
        if not SCRAPING_DEPS_AVAILABLE:
            return None
            
        if not self.session:
            connector = aiohttp.TCPConnector(limit=settings.MAX_CONCURRENT_REQUESTS)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": self.ua.random if settings.USER_AGENTS_ROTATE else self.ua.chrome}
            )
        return self.session
    
    def get_driver(self):
        """Get Selenium Chrome driver"""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available, skipping Chrome driver")
            return None
            
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={self.ua.random}")
        
        try:
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            return None
    
    async def scrape_deals(self):
        """Main scraping method"""
        if not SCRAPING_DEPS_AVAILABLE:
            logger.warning("Scraping dependencies not available. Skipping scraping.")
            return
            
        logger.info("Starting deal scraping...")
        
        for region in settings.amazon_regions_list:
            try:
                await self.scrape_region_deals(region)
                await asyncio.sleep(random.uniform(
                    settings.REQUEST_DELAY_MIN, 
                    settings.REQUEST_DELAY_MAX
                ))
            except Exception as e:
                logger.error(f"Error scraping {region}: {e}")
        
        logger.info("Deal scraping completed")
    
    async def scrape_region_deals(self, region: str):
        """Scrape deals for a specific region"""
        base_urls = {
            "US": "https://www.amazon.com",
            "UK": "https://www.amazon.co.uk",
            "CA": "https://www.amazon.ca",
            "DE": "https://www.amazon.de",
            "FR": "https://www.amazon.fr",
            "ES": "https://www.amazon.es",
            "IT": "https://www.amazon.it",
            "JP": "https://www.amazon.co.jp"
        }
        
        base_url = base_urls.get(region, base_urls["US"])
        
        # Scrape different deal types
        await self.scrape_lightning_deals(base_url, region)
        await self.scrape_best_sellers(base_url, region)
        await self.scrape_deals_page(base_url, region)
    
    async def scrape_lightning_deals(self, base_url: str, region: str):
        """Scrape lightning deals"""
        try:
            url = f"{base_url}/gp/goldbox"
            session = await self.get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find lightning deal containers
                    deal_containers = soup.find_all('div', {'data-testid': re.compile('grid-deals-container')})
                    
                    for container in deal_containers:
                        await self.extract_deal_info(container, base_url, region, is_lightning=True)
                        
        except Exception as e:
            logger.error(f"Error scraping lightning deals for {region}: {e}")
    
    async def scrape_best_sellers(self, base_url: str, region: str):
        """Scrape best sellers"""
        try:
            categories = ['electronics', 'home-garden', 'sports-outdoors', 'toys-games']
            
            for category in categories:
                url = f"{base_url}/gp/bestsellers/{category}"
                session = await self.get_session()
                
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find product containers
                        products = soup.find_all('div', {'data-component-type': 'item'})
                        
                        for product in products[:20]:  # Limit to top 20
                            await self.extract_bestseller_info(product, base_url, region, category)
                            
                await asyncio.sleep(random.uniform(1, 2))
                
        except Exception as e:
            logger.error(f"Error scraping best sellers for {region}: {e}")
    
    async def scrape_deals_page(self, base_url: str, region: str):
        """Scrape general deals page"""
        try:
            url = f"{base_url}/s?k=deals&ref=sr_pg_1"
            session = await self.get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find product containers
                    products = soup.find_all('div', {'data-component-type': 's-search-result'})
                    
                    for product in products:
                        await self.extract_search_result_info(product, base_url, region)
                        
        except Exception as e:
            logger.error(f"Error scraping deals page for {region}: {e}")
    
    async def extract_deal_info(self, container, base_url: str, region: str, is_lightning: bool = False):
        """Extract deal information from container"""
        try:
            # Extract basic info
            title_elem = container.find('span', {'data-testid': 'deal-title'})
            if not title_elem:
                return
                
            title = title_elem.get_text(strip=True)
            
            # Extract ASIN
            link_elem = container.find('a', href=True)
            if not link_elem:
                return
                
            product_url = urljoin(base_url, link_elem['href'])
            asin = self.extract_asin_from_url(product_url)
            if not asin:
                return
            
            # Extract pricing
            price_elem = container.find('span', {'class': re.compile('a-price-whole')})
            if not price_elem:
                return
                
            current_price = self.parse_price(price_elem.get_text(strip=True))
            
            # Extract discount
            discount_elem = container.find('span', {'class': re.compile('a-label-discount')})
            discount_percentage = 0
            if discount_elem:
                discount_text = discount_elem.get_text(strip=True)
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    discount_percentage = int(discount_match.group(1))
            
            # Skip if discount is too low
            if discount_percentage < settings.MIN_DISCOUNT_PERCENTAGE:
                return
            
            # Extract image
            img_elem = container.find('img')
            image_url = img_elem.get('src') if img_elem else None
            
            # Calculate original price
            original_price = current_price / (1 - discount_percentage / 100) if discount_percentage > 0 else current_price
            
            # Create affiliate URL
            affiliate_url = await self.affiliate_service.create_affiliate_url(product_url, region)
            
            # Save to database
            await self.save_product(
                asin=asin,
                title=title,
                current_price=current_price,
                original_price=original_price,
                discount_percentage=discount_percentage,
                product_url=product_url,
                affiliate_url=affiliate_url,
                image_url=image_url,
                region=region,
                is_lightning_deal=is_lightning,
                category="deals"
            )
            
        except Exception as e:
            logger.error(f"Error extracting deal info: {e}")
    
    async def extract_bestseller_info(self, product, base_url: str, region: str, category: str):
        """Extract bestseller information"""
        try:
            # Extract title
            title_elem = product.find('span', {'class': re.compile('a-size-mini')})
            if not title_elem:
                return
                
            title = title_elem.get_text(strip=True)
            
            # Extract link and ASIN
            link_elem = product.find('a', href=True)
            if not link_elem:
                return
                
            product_url = urljoin(base_url, link_elem['href'])
            asin = self.extract_asin_from_url(product_url)
            if not asin:
                return
            
            # Extract price
            price_elem = product.find('span', {'class': 'a-price-whole'})
            if not price_elem:
                return
                
            current_price = self.parse_price(price_elem.get_text(strip=True))
            
            # Extract rating
            rating_elem = product.find('span', {'class': 'a-icon-alt'})
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Skip if rating is too low
            if rating < settings.MIN_PRODUCT_RATING:
                return
            
            # Extract image
            img_elem = product.find('img')
            image_url = img_elem.get('src') if img_elem else None
            
            # Create affiliate URL
            affiliate_url = await self.affiliate_service.create_affiliate_url(product_url, region)
            
            # Save to database
            await self.save_product(
                asin=asin,
                title=title,
                current_price=current_price,
                original_price=current_price,
                discount_percentage=0,
                product_url=product_url,
                affiliate_url=affiliate_url,
                image_url=image_url,
                region=region,
                category=category,
                rating=rating,
                is_trending=True
            )
            
        except Exception as e:
            logger.error(f"Error extracting bestseller info: {e}")
    
    async def extract_search_result_info(self, product, base_url: str, region: str):
        """Extract search result information"""
        try:
            # Similar to extract_bestseller_info but for search results
            # Implementation details...
            pass
            
        except Exception as e:
            logger.error(f"Error extracting search result info: {e}")
    
    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL"""
        asin_match = re.search(r'/([A-Z0-9]{10})', url)
        return asin_match.group(1) if asin_match else None
    
    def parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        # Remove currency symbols and parse
        price_cleaned = re.sub(r'[^\d.,]', '', price_text)
        price_cleaned = price_cleaned.replace(',', '')
        try:
            return float(price_cleaned)
        except ValueError:
            return 0.0
    
    async def save_product(self, **product_data):
        """Save product to database"""
        try:
            async with AsyncSessionLocal() as session:
                # Check if product already exists
                existing = await session.get(Product, product_data['asin'])
                
                if existing:
                    # Update existing product
                    for key, value in product_data.items():
                        setattr(existing, key, value)
                    existing.scraped_at = datetime.utcnow()
                else:
                    # Create new product
                    product = Product(**product_data)
                    session.add(product)
                
                await session.commit()
                logger.debug(f"Saved product: {product_data['title']}")
                
        except Exception as e:
            logger.error(f"Error saving product: {e}")
    
    async def close(self):
        """Close resources"""
        if self.session:
            await self.session.close()
