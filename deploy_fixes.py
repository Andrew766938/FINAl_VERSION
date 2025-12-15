#!/usr/bin/env python3
import requests
import base64
import json

TOKEN = "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"
REPO = "Andrew766938/FINAL_VERSION"

# API роутеры с исправленными импортами
FILES = {
    "app/api/posts.py": '''from fastapi import APIRouter, Depends, status
from app.api.dependencies import DBDep, get_current_user
from app.services.posts import PostService
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.models.users import UserModel

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate, db: DBDep, current_user: UserModel = Depends(get_current_user)):
    service = PostService(db)
    return await service.create_post(post_data, current_user.id)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: DBDep):
    service = PostService(db)
    return await service.get_post(post_id)

@router.get("/", response_model=list[PostResponse])
async def get_all_posts(skip: int = 0, limit: int = 10, db: DBDep = Depends()):
    service = PostService(db)
    return await service.get_all_posts(skip, limit)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate, db: DBDep, current_user: UserModel = Depends(get_current_user)):
    service = PostService(db)
    return await service.update_post(post_id, post_data, current_user.id)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: DBDep, current_user: UserModel = Depends(get_current_user)):
    service = PostService(db)
    await service.delete_post(post_id, current_user.id)
    return None
'''}]


def get_file_sha(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def update_file(path, content, message):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
    
    # Кодируем в base64
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    data = {"message": message, "content": content_b64}
    
    # Если файл существует, нужен SHA
    sha = get_file_sha(path)
    if sha:
        data["sha"] = sha
    
    r = requests.put(url, headers=headers, data=json.dumps(data))
    if r.status_code in [200, 201]:
        print(f"✅ {path}")
        return True
    else:
        print(f"❌ {path}: {r.status_code} - {r.text[:200]}")
        return False

print("🚀 Начинаю деплой...")
for path, content in FILES.items():
    update_file(path, content, f"Fix {path} - correct imports and dependencies")

print("\n✅ Все файлы обновлены!")
