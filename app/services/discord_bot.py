"""
Discord bot service
"""

import logging
from typing import Optional
import asyncio
import discord
from discord.ext import commands

from app.core.config import settings

logger = logging.getLogger(__name__)


class DiscordBot:
    def __init__(self):
        self.bot = None
        self.channel_id = None
        
        if settings.DISCORD_BOT_TOKEN:
            intents = discord.Intents.default()
            intents.message_content = True
            self.bot = commands.Bot(command_prefix='!', intents=intents)
            
        if settings.DISCORD_CHANNEL_ID:
            self.channel_id = int(settings.DISCORD_CHANNEL_ID)
    
    async def send_deal(self, message: str, product) -> bool:
        """Send deal to Discord channel"""
        if not self.bot or not self.channel_id:
            logger.warning("Discord bot not configured")
            return False
            
        try:
            # Login if not already connected
            if not self.bot.is_ready():
                await self.bot.login(settings.DISCORD_BOT_TOKEN)
            
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Discord channel {self.channel_id} not found")
                return False
            
            # Create embed for better formatting
            embed = discord.Embed(
                title=product.title,
                description=message,
                color=0x00ff00 if product.discount_percentage > 30 else 0xff9900
            )
            
            if product.image_url:
                embed.set_thumbnail(url=product.image_url)
            
            embed.add_field(
                name="Price", 
                value=f"${product.current_price:.2f}", 
                inline=True
            )
            
            if product.discount_percentage > 0:
                embed.add_field(
                    name="Discount", 
                    value=f"{product.discount_percentage}%", 
                    inline=True
                )
            
            if product.rating:
                embed.add_field(
                    name="Rating", 
                    value=f"⭐ {product.rating}/5", 
                    inline=True
                )
            
            embed.add_field(
                name="Buy Now", 
                value=f"[Amazon Link]({product.affiliate_url})", 
                inline=False
            )
            
            await channel.send(embed=embed)
            logger.info(f"Sent Discord message for: {product.title}")
            return True
            
        except discord.errors.DiscordException as e:
            logger.error(f"Discord error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return False
    
    async def send_message(self, text: str, channel_id: Optional[int] = None) -> bool:
        """Send simple text message"""
        if not self.bot:
            return False
            
        target_channel = channel_id or self.channel_id
        if not target_channel:
            return False
            
        try:
            if not self.bot.is_ready():
                await self.bot.login(settings.DISCORD_BOT_TOKEN)
                
            channel = self.bot.get_channel(target_channel)
            if channel:
                await channel.send(text)
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return False
