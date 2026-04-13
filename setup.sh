#!/bin/bash

# Giggle — AI Joke Engine Setup Script

set -e

echo "🎭 Setting up Giggle — AI Joke Engine"
echo "======================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo ""
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Created Python virtual environment"
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
echo "✅ Installed Python dependencies"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "⚠️  Created .env file - PLEASE EDIT IT AND ADD YOUR OPENAI_API_KEY"
    echo "   File location: backend/.env"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
alembic upgrade head
echo "✅ Database initialized"

cd ..

echo ""
echo "📦 Setting up Frontend..."
cd frontend

# Install dependencies
npm install
echo "✅ Installed Node dependencies"

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit backend/.env and add your OPENAI_API_KEY"
echo "   2. Start the backend:"
echo "      cd backend && source .venv/bin/activate && uvicorn main:app --reload"
echo "   3. In a new terminal, start the frontend:"
echo "      cd frontend && npm run dev"
echo "   4. Open http://localhost:5173 in your browser"
echo ""
echo "🎉 Happy joke generating!"
