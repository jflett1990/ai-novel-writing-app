# Server Startup Guide

## Quick Start Commands

### Backend Server
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/backend && python3 app.py
```

### Frontend Server
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/frontend && npm start
```
If port 3000 is in use, type `Y` when prompted to use another port.

## Detailed Steps

### 1. Backend Server (FastAPI)

**Location**: `ai_novel_app/backend/`
**Port**: 8000
**Command**: 
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/backend && python3 app.py
```

**What happens:**
- Uses system Python 3 (not the broken venv)
- Starts uvicorn server with auto-reload
- Creates/verifies database tables
- Runs on http://localhost:8000
- API docs available at http://localhost:8000/docs

**If port 8000 is in use:**
```bash
# Kill existing process on port 8000
lsof -ti:8000 | xargs kill -9
# Then start normally
cd /Users/jamesfletty/finalbook/ai_novel_app/backend && python3 app.py
```

### 2. Frontend Server (React)

**Location**: `ai_novel_app/frontend/`
**Port**: 3001 (or next available)
**Command**:
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/frontend && npm start
```

**What happens:**
- Starts React development server
- If port 3000 is busy, prompts to use another port
- Type `Y` to accept alternative port
- Usually runs on http://localhost:3001

## Troubleshooting

### Backend Issues

**Problem**: `Error loading ASGI app. Could not import module "app"`
**Solution**: Make sure you're in the correct directory:
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/backend
```

**Problem**: `Address already in use`
**Solution**: Kill the process using port 8000:
```bash
lsof -ti:8000 | xargs kill -9
```

**Problem**: Virtual environment issues
**Solution**: Use system Python 3 instead of the broken venv:
```bash
python3 app.py  # NOT ./venv/bin/python
```

### Frontend Issues

**Problem**: Port 3000 in use
**Solution**: Type `Y` when prompted to use another port

**Problem**: `npm start` not found
**Solution**: Make sure you're in the frontend directory:
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/frontend
```

## Environment Configuration

The backend uses these settings from `.env`:
- **AI Provider**: Ollama (cogito:14b model)
- **Database**: SQLite (ai_novel_app.db)
- **Complexity**: Literary
- **CORS**: Allows localhost:3000, 3001, 3002

## Verification

### Backend Running Successfully:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
Database tables created/verified
```

### Frontend Running Successfully:
```
Compiled successfully!
You can now view frontend in the browser.
Local: http://localhost:3001
```

## One-Line Startup (Both Servers)

**Terminal 1 (Backend):**
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/backend && python3 app.py
```

**Terminal 2 (Frontend):**
```bash
cd /Users/jamesfletty/finalbook/ai_novel_app/frontend && npm start
```

## URLs After Startup

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Notes

- The venv in backend/ has broken symlinks - use system Python 3 instead
- Frontend will auto-detect port conflicts and offer alternatives
- Backend auto-reloads on code changes
- Frontend auto-reloads on code changes
- Both servers need to be running for the app to work properly

## Common Mistakes to Avoid

1. ❌ Don't try to use `./venv/bin/python` - it's broken
2. ❌ Don't run from wrong directory - use full paths
3. ❌ Don't forget to kill existing processes on ports 8000/3000
4. ❌ Don't use `uvicorn` directly - use `python3 app.py`
5. ✅ Always use the full path commands above
