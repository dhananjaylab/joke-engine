# Frontend Restart Guide

## The Issue
The frontend styling wasn't showing because:
1. Tailwind CSS directives (`@tailwind base`, `@tailwind components`, `@tailwind utilities`) were missing from `index.css`
2. The development server needed to be restarted to pick up the new Tailwind configuration
3. The `dark` class needed to be added to the HTML element

## What Was Fixed
1. ✅ Added Tailwind directives to `frontend/src/index.css`
2. ✅ Added `class="dark"` to the `<html>` tag in `frontend/index.html`
3. ✅ Updated `tailwind.config.ts` with safelist for gold colors
4. ✅ Updated theme color in manifest to match dark theme

## How to Restart the Frontend

### Option 1: Using the Batch Script (Windows)
```bash
cd frontend
restart-dev.bat
```

### Option 2: Manual Restart
```bash
# Stop any running dev servers
# Press Ctrl+C in the terminal running the dev server

# Navigate to frontend directory
cd frontend

# Clear Vite cache (optional but recommended)
rm -rf node_modules/.vite

# Start the development server
npm run dev
```

### Option 3: Kill Process and Restart
```bash
# Kill all node processes (Windows)
taskkill /F /IM node.exe

# Navigate to frontend
cd frontend

# Start dev server
npm run dev
```

## Verify the Changes

After restarting, you should see:
- ✅ Dark background (zinc-950)
- ✅ Gold "GIGGLE" logo in the navbar
- ✅ Gold "GENERATE ⚡" button
- ✅ Status badges at the top
- ✅ Trending topic chips
- ✅ Two-column layout with Reverse Heckler and Top Rated sections
- ✅ Bottom navigation on mobile

## If Styles Still Don't Load

1. **Hard refresh the browser**: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. **Clear browser cache**: Open DevTools (F12) → Network tab → Check "Disable cache"
3. **Check the browser console**: Look for any CSS loading errors
4. **Verify Tailwind is working**: Inspect an element and check if Tailwind classes are applied

## Common Issues

### Issue: "Cannot find module 'tailwindcss'"
**Solution**: Install dependencies
```bash
cd frontend
npm install
```

### Issue: Styles not updating
**Solution**: Clear Vite cache
```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

### Issue: Port already in use
**Solution**: Kill the process or use a different port
```bash
# Kill process on port 5173 (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use a different port
npm run dev -- --port 5174
```

## Development Server Info

- **Default URL**: http://localhost:5173
- **Network URL**: Will be shown in terminal (for testing on mobile)
- **Hot Module Replacement**: Enabled (changes reflect immediately)

## Next Steps

Once the server is running and styles are loading:
1. Test the responsive design (resize browser window)
2. Test mobile navigation (bottom nav should appear on small screens)
3. Try generating a joke to see the streaming animation
4. Check the History and Profile pages
