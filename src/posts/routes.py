from datetime import datetime, timedelta
import fastapi
from fastapi.params import Query 
from src.posts.models import User
from src.auth.service import Auth
import src.posts.schemas as schemas
import src.posts.models as models
from database import get_db

router = fastapi.APIRouter(prefix="/posts", tags=["posts"])

auth_service = Auth()

@router.get("/getPosts")
async def get_post(
    id: int = None,
    name: str = None,
    text: str = None,
    db=fastapi.Depends(get_db),
    current_user: User = fastapi.Depends(auth_service.get_current_user)):
    
    query = db.query(models.PostModel).filter(models.PostModel.user_id == current_user.id)
    
    if id is not None:
        query = query.filter(models.PostModel.id == id)
    if name:
        query = query.filter(models.PostModel.name == name)
    if text:
        query = query.filter(models.PostModel.text == text)
    
    post = query.first()
    if not post:
        return {"error": "Contact not found"}

    return post

@router.get("/")
async def get_posts(db = fastapi.Depends(get_db), current_user: User = fastapi.Depends(auth_service.get_current_user)):
    posts = db.query(models.PostModel).filter(models.PostModel.user_id == current_user.id).all()
    
    return posts

@router.post("/")
async def addPost(post: schemas.PostRequestSchema, db = fastapi.Depends(get_db), current_user: User = fastapi.Depends(auth_service.get_current_user)):
    new_post = models.PostModel(
        name=post.name,
        text=post.text,
        user_id=current_user.id 
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    new_post.user.hash_password = None
    new_post.user.refresh_token = None
    return new_post

@router.put("/{id}")
async def update_contact(
    id: int,
    post: schemas.PostRequestSchema,
    db = fastapi.Depends(get_db),
    current_user: User = fastapi.Depends(auth_service.get_current_user)
):
    db_post = db.query(models.PostModel).filter(models.PostModel.id == id).first()

    if db_post and db_post.user_id == current_user.id:
        db_post.name = post.name
        db_post.text = post.text
        

        db.commit()
        return {"message": "Post updated successfully"}

    return {"error": "Post not found or does not belong to the current user"}

@router.delete("/{id}")
async def deletePost(id: int, db = fastapi.Depends(get_db), current_user: User = fastapi.Depends(auth_service.get_current_user)):
    post = db.query(models.PostModel).filter(models.PostModel.id == id).first()
    if post and post.user_id == current_user.id:
        db.delete(post)
        db.commit()
        return post
    return {"error": "Post not found or does not belong to the current user"}