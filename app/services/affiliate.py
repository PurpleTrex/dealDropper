"""
Affiliate link management service
"""

import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional
import aiohttp

from app.core.config import settings

logger = logging.getLogger(__name__)


class AffiliateService:
    def __init__(self):
        self.associate_ids = {
            "US": settings.AMAZON_ASSOCIATES_ID,
            "UK": settings.AMAZON_ASSOCIATES_ID + "-21",
            "CA": settings.AMAZON_ASSOCIATES_ID + "-20",
            "DE": settings.AMAZON_ASSOCIATES_ID + "-21",
            "FR": settings.AMAZON_ASSOCIATES_ID + "-21",
            "ES": settings.AMAZON_ASSOCIATES_ID + "-21",
            "IT": settings.AMAZON_ASSOCIATES_ID + "-21",
            "JP": settings.AMAZON_ASSOCIATES_ID + "-22"
        }
    
    async def create_affiliate_url(self, product_url: str, region: str = "US") -> str:
        """Create affiliate URL with associate ID"""
        try:
            parsed_url = urlparse(product_url)
            query_params = parse_qs(parsed_url.query)
            
            # Add associate tag
            associate_id = self.associate_ids.get(region, self.associate_ids["US"])
            if associate_id:
                query_params['tag'] = [associate_id]
            
            # Add tracking parameters
            query_params['linkCode'] = ['as2']
            query_params['camp'] = ['1789']
            query_params['creative'] = ['9325']
            
            # Rebuild URL
            new_query = urlencode(query_params, doseq=True)
            affiliate_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            return affiliate_url
            
        except Exception as e:
            logger.error(f"Error creating affiliate URL: {e}")
            return product_url
    
    async def shorten_url(self, url: str) -> str:
        """Shorten URL using configured service"""
        if not settings.BITLY_ACCESS_TOKEN:
            return url
            
        try:
            headers = {
                'Authorization': f'Bearer {settings.BITLY_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'long_url': url,
                'domain': 'bit.ly'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api-ssl.bitly.com/v4/shorten',
                    json=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('link', url)
                    else:
                        logger.error(f"Bitly API error: {response.status}")
                        return url
                        
        except Exception as e:
            logger.error(f"Error shortening URL: {e}")
            return url
    
    def extract_commission_rate(self, category: str) -> float:
        """Get commission rate based on category"""
        rates = {
            'electronics': 0.02,
            'toys-games': 0.03,
            'sports-outdoors': 0.03,
            'home-garden': 0.04,
            'beauty': 0.04,
            'books': 0.04,
            'fashion': 0.05,
            'jewelry': 0.06,
            'luxury': 0.10
        }
        return rates.get(category.lower(), 0.02)  # Default 2%
