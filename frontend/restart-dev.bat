@echo off
echo Stopping any running dev servers...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo Cleaning build cache...
if exist node_modules\.vite rmdir /s /q node_modules\.vite

echo Starting development server...
npm run dev
