#!/bin/bash

# NikAssistant Start Script
# This script starts the NikAssistant application

echo "🧠 Starting NikAssistant..."
echo "============================"

# Check if virtual environment exists
if [ ! -d "nikassistant_env" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source nikassistant_env/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating basic configuration..."
    echo "📝 Please configure your credentials in .env file"
    
    # Create basic .env file
    cat > .env << EOF
# Email Configuration (Required for email notifications)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password

# Google Calendar API (Optional - for calendar integration)
GOOGLE_API_KEY=path/to/your/service-account-key.json
GOOGLE_CALENDAR_ID=primary

# Firebase (Optional - for mobile notifications)
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/firebase-key.json

# App Configuration
DEBUG=False
APP_PORT=8501
EOF
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please ensure you're in the correct directory."
    exit 1
fi

# Create necessary directories
mkdir -p data logs static/icons

# Get port from environment or use default
PORT=${APP_PORT:-8501}

# Check if port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is already in use. Trying alternative ports..."
    PORT=$((PORT + 1))
    while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; do
        PORT=$((PORT + 1))
        if [ $PORT -gt 8510 ]; then
            echo "❌ No available ports found in range 8501-8510"
            exit 1
        fi
    done
    echo "✅ Using port $PORT"
fi

# Export environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

echo "🌐 Starting NikAssistant on http://localhost:$PORT"
echo "⏹️  Press Ctrl+C to stop the application"
echo ""

# Start the application
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
