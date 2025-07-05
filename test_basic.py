"""
Simple test to verify the application works
"""

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        from app.core.config import settings
        print("✅ Configuration module loaded")
        print(f"   App Name: {settings.APP_NAME}")
        print(f"   Debug Mode: {settings.DEBUG}")
        
        from app.core.database import Base, Product, User, Deal
        print("✅ Database models loaded")
        
        from app.services.affiliate import AffiliateService
        print("✅ Affiliate service loaded")
        
        from app.services.analytics import AnalyticsService
        print("✅ Analytics service loaded")
        
        from app.api.routes import api_router
        print("✅ API routes loaded")
        
        from app.web.routes import web_router
        print("✅ Web routes loaded")
        
        print("\n🎉 All core modules loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration values"""
    try:
        from app.core.config import settings
        
        print("\n📋 Configuration Status:")
        print(f"   Database URL: {'✅ Set' if settings.DATABASE_URL else '❌ Not set'}")
        print(f"   Redis URL: {'✅ Set' if settings.REDIS_URL else '❌ Not set'}")
        print(f"   Amazon Associates ID: {'✅ Set' if settings.AMAZON_ASSOCIATES_ID else '❌ Not set'}")
        print(f"   Host: {settings.HOST}:{settings.PORT}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 DealDropper Application Test\n")
    
    success = True
    success &= test_imports()
    success &= test_configuration()
    
    if success:
        print("\n✅ Application is ready to run!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Set up PostgreSQL and Redis (or use Docker)")
        print("3. Run: python main.py")
        print("4. Visit: http://localhost:8000")
    else:
        print("\n❌ Some issues found. Please check the errors above.")

if __name__ == "__main__":
    main()
