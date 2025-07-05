# DealDropper - Production-Grade Amazon Deal Tracker

A comprehensive, automated deal-tracking ecosystem that monitors Amazon for price drops, trending products, and lightning deals. Distributes deals through multiple channels with affiliate link integration for revenue generation.

## Features

- 🔍 Smart Amazon price scraping and deal detection
- 🤖 Automated distribution to Telegram, Discord, Twitter, Email
- 💰 Amazon affiliate link integration
- 📱 Web frontend and mobile-ready interface
- 📊 Admin dashboard with analytics
- 🔔 Real-time notifications and alerts
- 💾 PostgreSQL + Redis database stack
- 🚀 Production-ready with Docker deployment

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run Database Migrations**
   ```bash
   python scripts/init_db.py
   ```

4. **Start the Application**
   ```bash
   python main.py
   ```

5. **Access the Dashboard**
   - Web App: http://localhost:8000
   - Admin Dashboard: http://localhost:8000/admin

## Environment Variables

See `.env.example` for all required configuration variables.

## Architecture

- **Backend**: FastAPI with async support
- **Database**: PostgreSQL with Redis caching
- **Scraping**: BeautifulSoup + Selenium
- **Scheduling**: APScheduler
- **Frontend**: Modern HTML/CSS/JS with Tailwind CSS

## License

MIT License - see LICENSE file for details.
