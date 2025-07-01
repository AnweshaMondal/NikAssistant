#!/bin/bash

# NikAssistant Setup Script
# This script sets up the NikAssistant environment

echo "🧠 Setting up NikAssistant..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "nikassistant_env" ]; then
    python3 -m venv nikassistant_env
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source nikassistant_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create .env file if it doesn't exist
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f "example.env" ]; then
        cp example.env .env
        echo "✅ Created .env file from example.env"
        echo "📝 Please edit .env file with your actual credentials"
    else
        echo "⚠️  example.env not found, creating basic .env file"
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
        echo "✅ Created basic .env file"
    fi
else
    echo "ℹ️  .env file already exists"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data logs static/icons
echo "✅ Data directories created"

# Initialize data files
echo "🗄️  Initializing data files..."
python3 -c "
import json
import os

# Create tasks.json if it doesn't exist
if not os.path.exists('data/tasks.json'):
    with open('data/tasks.json', 'w') as f:
        json.dump({'tasks': []}, f, indent=4)
    print('✅ Created data/tasks.json')

# Create notes.json if it doesn't exist
if not os.path.exists('data/notes.json'):
    with open('data/notes.json', 'w') as f:
        json.dump({'notes': []}, f, indent=4)
    print('✅ Created data/notes.json')

# Create calendar.json if it doesn't exist
if not os.path.exists('data/calendar.json'):
    with open('data/calendar.json', 'w') as f:
        json.dump({'events': []}, f, indent=4)
    print('✅ Created data/calendar.json')
"

# Check for optional dependencies
echo "🔍 Checking optional dependencies..."

# Check for audio dependencies (for speech recognition)
echo "🎤 Checking audio dependencies for speech recognition..."
if python3 -c "import pyaudio" 2>/dev/null; then
    echo "✅ PyAudio is available for speech recognition"
else
    echo "⚠️  PyAudio not available. Speech recognition may not work."
    echo "   To install on Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio"
    echo "   To install on macOS: brew install portaudio"
fi

# Make start script executable
echo "🔧 Making start script executable..."
chmod +x start.sh 2>/dev/null || echo "⚠️  Could not make start.sh executable"

# Test basic imports
echo "🧪 Testing basic imports..."
python3 -c "
try:
    import streamlit
    import pandas
    import numpy
    import plotly
    print('✅ Core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================="
echo ""
echo "📋 Next steps:"
echo "1. Edit the .env file with your actual credentials:"
echo "   - Gmail app password for email notifications"
echo "   - Google Calendar API key for calendar integration"
echo "   - Firebase key for mobile notifications (optional)"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "📖 For detailed configuration instructions, see README.md"
echo ""
echo "🚀 Happy productivity with NikAssistant!"
