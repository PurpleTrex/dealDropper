#!/bin/bash

echo "Starting DealDropper Application Setup..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Please edit .env file with your API keys and configuration"
    echo
fi

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

# Run tests
echo "Running application tests..."
python scripts/test_app.py

echo
echo "Setup complete! You can now start the application with:"
echo "python main.py"
echo
echo "Or run the scraper manually with:"
echo "python scripts/run_scraper.py scrape"
echo
