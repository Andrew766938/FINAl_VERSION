import os
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.friendships import router as friendships_router
from app.api.comments import router as comments_router
from app.api.likes import router as likes_router
from app.api.friends import router as friends_router  # NEW
from app.config import settings
from app.database.database import Base
from app.services.data_init import init_sample_data
from app.admin import setup_admin

app = FastAPI(title="Betony", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "app", "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    frontend_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Betony API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    """Create database tables and initialize sample data on startup"""
    print("[APP] Starting application...")
    print("[APP] Creating database tables...")
    try:
        engine = create_async_engine(settings.get_db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[APP] Database tables created successfully!")
        
        # Initialize sample data
        print("[APP] Initializing sample data...")
        await init_sample_data()
        print("[APP] Sample data initialized successfully!")
        
        # Setup SQLAdmin
        print("[APP] Setting up admin panel...")
        try:
            setup_admin(app, engine)
            print("[APP] 🎉 Admin panel available at: http://localhost:8000/admin")
        except Exception as e:
            print(f"[APP] ⚠️  Could not setup admin panel: {e}")
        
        await engine.dispose()
    except Exception as e:
        print(f"[APP] Error during startup: {e}")
        import traceback
        traceback.print_exc()


# Include routers
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(friendships_router)
app.include_router(friends_router)  # NEW


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=True)
