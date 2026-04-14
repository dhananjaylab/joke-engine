@echo off
REM Giggle — AI Joke Engine Setup Script for Windows

echo 🎭 Setting up Giggle — AI Joke Engine
echo ======================================

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed.
    exit /b 1
)

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    exit /b 1
)

echo.
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment
if not exist ".venv" (
    python -m venv .venv
    echo ✅ Created Python virtual environment
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt
echo ✅ Installed Python dependencies

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.template .env
    echo ⚠️  Created .env file - PLEASE EDIT IT AND ADD YOUR OPENAI_API_KEY
    echo    File location: backend\.env
)

REM Initialize database
echo.
echo 🗄️  Initializing database...
alembic upgrade head
echo ✅ Database initialized

cd ..

echo.
echo 📦 Setting up Frontend...
cd frontend

REM Install dependencies
call npm install
echo ✅ Installed Node dependencies

cd ..

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo    1. Edit backend\.env and add your OPENAI_API_KEY
echo    2. Start the backend:
echo       cd backend ^&^& .venv\Scripts\activate ^&^& uvicorn main:app --reload
echo    3. In a new terminal, start the frontend:
echo       cd frontend ^&^& npm run dev
echo    4. Open http://localhost:5173 in your browser
echo.
echo 🎉 Happy joke generating!
pause
