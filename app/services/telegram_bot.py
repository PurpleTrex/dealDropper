"""
Telegram bot service
"""

import logging
from typing import Optional
import asyncio
from telegram import Bot
from telegram.error import TelegramError

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.bot = None
        if settings.TELEGRAM_BOT_TOKEN:
            self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.chat_id = settings.TELEGRAM_CHAT_ID
    
    async def send_deal(self, message: str, product) -> bool:
        """Send deal to Telegram channel"""
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured")
            return False
            
        try:
            # Send message with image if available
            if product.image_url:
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=product.image_url,
                    caption=message,
                    parse_mode='HTML'
                )
            else:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML'
                )
            
            logger.info(f"Sent Telegram message for: {product.title}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def send_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        """Send simple text message"""
        if not self.bot:
            return False
            
        target_chat = chat_id or self.chat_id
        if not target_chat:
            return False
            
        try:
            await self.bot.send_message(
                chat_id=target_chat,
                text=text,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
