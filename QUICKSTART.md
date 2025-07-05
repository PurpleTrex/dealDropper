# DealDropper - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- Redis server
- Git

### Quick Setup

1. **Clone and Setup**
   ```bash
   # Windows
   setup.bat
   
   # Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure Environment**
   Edit `.env` file with your API keys:
   ```env
   # Required - Amazon Associates
   AMAZON_ASSOCIATES_ID=your-associates-id
   
   # Social Media (Optional)
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   DISCORD_BOT_TOKEN=your-discord-bot-token
   TWITTER_API_KEY=your-twitter-api-key
   
   # Email (Optional)
   SENDGRID_API_KEY=your-sendgrid-api-key
   ```

3. **Start the Application**
   ```bash
   python main.py
   ```

4. **Access the App**
   - Web App: http://localhost:8000
   - Admin Dashboard: http://localhost:8000/admin
   - API Docs: http://localhost:8000/docs

## 🔧 Manual Operations

### Run Scraper
```bash
# Scrape deals only
python scripts/run_scraper.py scrape

# Distribute deals only
python scripts/run_scraper.py distribute

# Both operations
python scripts/run_scraper.py both
```

### Test Application
```bash
python scripts/test_app.py
```

## 📊 Features Overview

### ✅ Implemented Features
- **Web Scraping**: Amazon deal detection with multiple strategies
- **Database**: PostgreSQL with Redis caching
- **Web Interface**: Modern responsive design
- **Admin Dashboard**: Real-time analytics and management
- **API**: RESTful API with FastAPI
- **Affiliate Links**: Automatic Amazon Associates integration
- **Multi-channel Distribution**: Ready for Telegram, Discord, Twitter
- **Email Service**: Newsletter and notifications
- **Analytics**: Performance tracking and metrics
- **Automated Scheduling**: Background tasks with APScheduler

### 🎯 Core Functionality
1. **Deal Aggregation**: Scrapes lightning deals, best sellers, and discounted items
2. **Smart Filtering**: Filters by discount percentage, rating, price, and category
3. **Affiliate Integration**: Automatically adds affiliate tags to Amazon links
4. **Multi-channel Posting**: Distributes deals across social platforms
5. **User Management**: Email subscriptions and preferences
6. **Real-time Dashboard**: Monitor performance and manage settings

## 🔌 API Endpoints

### Public API
- `GET /api/deals` - Get latest deals
- `GET /api/products` - Get products
- `GET /api/trending` - Get trending products
- `GET /api/search?q=keyword` - Search deals
- `POST /api/subscribe` - Subscribe to alerts

### Admin API
- `GET /api/stats` - Dashboard statistics
- `GET /api/categories` - Available categories

## 🎨 Web Interface

### Pages
- **Home** (`/`) - Latest deals and trending products
- **Deals** (`/deals`) - All deals with filtering
- **Search** (`/search`) - Deal search functionality
- **Subscribe** (`/subscribe`) - Email subscription
- **Admin** (`/admin`) - Dashboard and analytics

## 🤖 Automation

The application includes automated tasks:
- **Scraping**: Every 15 minutes (configurable)
- **Distribution**: Every 5 minutes (configurable)
- **Analytics**: Daily metrics collection
- **Cleanup**: Removes old data periodically

## 💰 Monetization Ready

- **Amazon Associates**: Commission-based affiliate links
- **Email Marketing**: Newsletter subscriber management
- **Premium Features**: User tier system
- **Analytics**: Revenue tracking capabilities

## 🔒 Security Features

- **Input Validation**: Pydantic schemas
- **Rate Limiting**: Built-in request limiting
- **Environment Variables**: Secure configuration
- **CORS Protection**: Cross-origin request security

## 🚀 Deployment Options

### Docker
```bash
docker-compose up -d
```

### Manual Deployment
1. Set up PostgreSQL and Redis
2. Configure environment variables
3. Run database migrations
4. Start the application

## 📈 Scaling Considerations

- **Database**: PostgreSQL with proper indexing
- **Caching**: Redis for performance
- **Task Queue**: APScheduler for background jobs
- **Load Balancing**: Nginx configuration included
- **Monitoring**: Health checks and logging

## 🛠️ Development

### Project Structure
```
app/
├── api/          # API routes and schemas
├── core/         # Configuration and database
├── services/     # Business logic
├── templates/    # HTML templates
└── web/          # Web routes

scripts/          # Utility scripts
static/           # Static files
```

### Adding New Features
1. Create service in `app/services/`
2. Add API routes in `app/api/`
3. Update templates if needed
4. Add tests

This is a production-ready application with comprehensive features for Amazon deal tracking and distribution!
