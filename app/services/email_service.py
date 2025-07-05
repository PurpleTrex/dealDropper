"""
Email service for newsletters and notifications
"""

import logging
from typing import List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

from app.core.config import settings
from app.core.database import AsyncSessionLocal, User

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.sg = None
        if settings.SENDGRID_API_KEY:
            self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    async def send_newsletter(self, products: List) -> bool:
        """Send daily newsletter with top deals"""
        if not self.sg:
            logger.warning("SendGrid not configured")
            return False
            
        try:
            # Get all active users
            async with AsyncSessionLocal() as session:
                users = await session.execute("SELECT * FROM users WHERE is_active = true")
                user_list = users.fetchall()
            
            if not user_list:
                logger.info("No active users for newsletter")
                return True
            
            # Generate newsletter content
            html_content = self.generate_newsletter_html(products)
            
            # Send to all users
            for user in user_list:
                await self.send_email(
                    to_email=user.email,
                    subject=f"🔥 Today's Top Deals - {datetime.now().strftime('%B %d, %Y')}",
                    html_content=html_content
                )
            
            logger.info(f"Newsletter sent to {len(user_list)} users")
            return True
            
        except Exception as e:
            logger.error(f"Error sending newsletter: {e}")
            return False
    
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send individual email"""
        if not self.sg:
            return False
            
        try:
            from_email = Email(settings.FROM_EMAIL)
            to_email = To(to_email)
            content = Content("text/html", html_content)
            
            mail = Mail(from_email, to_email, subject, content)
            
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                logger.debug(f"Email sent to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def generate_newsletter_html(self, products: List) -> str:
        """Generate HTML newsletter content"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DealDropper - Today's Top Deals</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .deal-item {{ border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 10px; background: #fff; }}
                .deal-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .deal-price {{ font-size: 24px; color: #e74c3c; font-weight: bold; }}
                .deal-discount {{ background: #e74c3c; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px; }}
                .deal-rating {{ color: #f39c12; }}
                .deal-button {{ background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔥 DealDropper</h1>
                    <p>Today's Hottest Amazon Deals - {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="content">
        """
        
        for product in products[:10]:  # Top 10 deals
            stars = "⭐" * int(product.rating) if product.rating else ""
            discount_badge = f'<span class="deal-discount">{product.discount_percentage}% OFF</span>' if product.discount_percentage > 0 else ""
            
            html += f"""
                <div class="deal-item">
                    <div class="deal-title">{product.title}</div>
                    <div style="margin: 10px 0;">
                        <span class="deal-price">${product.current_price:.2f}</span>
                        {discount_badge}
                    </div>
                    {f'<div class="deal-rating">{stars} {product.rating}/5</div>' if product.rating else ''}
                    <a href="{product.affiliate_url}" class="deal-button">Get This Deal</a>
                </div>
            """
        
        html += f"""
                </div>
                
                <div class="footer">
                    <p>© 2025 DealDropper. All rights reserved.</p>
                    <p>You're receiving this because you subscribed to our deal alerts.</p>
                    <p><a href="#">Unsubscribe</a> | <a href="#">Manage Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def queue_deal(self, product) -> bool:
        """Queue deal for email notifications (placeholder)"""
        # This would typically add to a queue for batch processing
        logger.debug(f"Queued deal for email: {product.title}")
        return True
    
    async def send_welcome_email(self, user_email: str) -> bool:
        """Send welcome email to new subscribers"""
        subject = "Welcome to DealDropper! 🎉"
        html_content = f"""
        <h2>Welcome to DealDropper!</h2>
        <p>Thank you for subscribing to our deal alerts. You'll now receive the best Amazon deals delivered straight to your inbox.</p>
        <p>What you can expect:</p>
        <ul>
            <li>Daily newsletters with top deals</li>
            <li>Lightning deal alerts</li>
            <li>Exclusive discounts and promotions</li>
        </ul>
        <p>Happy shopping!</p>
        <p>The DealDropper Team</p>
        """
        
        return await self.send_email(user_email, subject, html_content)
