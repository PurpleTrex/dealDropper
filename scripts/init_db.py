"""
Database initialization script
"""

import asyncio
import logging
from app.core.database import init_db, AsyncSessionLocal, User
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create default admin user"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if admin user already exists
            result = await session.execute(
                "SELECT * FROM users WHERE email = :email",
                {"email": settings.ADMIN_EMAIL}
            )
            
            if not result.fetchone():
                admin_user = User(
                    email=settings.ADMIN_EMAIL,
                    is_premium=True,
                    is_active=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info(f"Created admin user: {settings.ADMIN_EMAIL}")
            else:
                logger.info("Admin user already exists")
                
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")


async def main():
    """Initialize database and create admin user"""
    logger.info("Initializing database...")
    
    try:
        await init_db()
        logger.info("Database tables created successfully")
        
        await create_admin_user()
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
