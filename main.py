import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.posts import router as posts_router
from app.api.comments import router as comments_router
from app.api.likes import router as likes_router
from app.api.friendships import router as friendships_router

app = FastAPI(title="Blog App", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "app", "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(friendships_router)


if __name__ == "__main__":
    uvicorn.run(app=app)
