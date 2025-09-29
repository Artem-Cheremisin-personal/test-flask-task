#!/bin/bash

# Cashabl Flask Application Startup Script

echo "🚀 Starting Cashabl Flask Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Creating from template..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your AWS and database credentials"
fi

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
python3 -c "import flask, boto3, psycopg2" 2>/dev/null || {
    echo "📥 Installing Python dependencies..."
    pip3 install -r requirements.txt
}

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the application
echo "🌟 Starting Flask application on http://localhost:5000"
echo "💡 Press Ctrl+C to stop the application"
echo "📊 Access transaction history at http://localhost:5000/transactions"
echo ""

python3 app.py
