from datetime import datetime, timedelta
import json
import fastapi
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query 
from src.posts.models import User
from src.auth.service import Auth
import src.posts.schemas as schemas
import src.posts.models as models
from database import get_db, SessionLocal

current_time = datetime.utcnow()
expiration_time = current_time + timedelta(minutes=10)

router = fastapi.APIRouter(prefix="/posts", tags=["posts"])

auth_service = Auth()

def get_cached_post(query_id):
    db = SessionLocal()
    cached_data = db.query(models.CachedData).filter(models.CachedData.query_id == str(query_id)).first()

    if cached_data and cached_data.expiration_time > datetime.utcnow():
        return json.loads(cached_data.query_result)
    return None

def cache_post(query_id, query_result, expiration_time):
    db = SessionLocal()
    
    query_result_list = [query_result] if isinstance(query_result, models.PostModel) else query_result
    serialized_result = json.dumps([post.to_dict() for post in query_result_list])
    
    db.add(models.CachedData(query_id=query_id, query_result=serialized_result, expiration_time=expiration_time))
    db.commit()

@router.get("/getPosts")
async def get_posts(db = fastapi.Depends(get_db), current_user: User = fastapi.Depends(auth_service.get_current_user)):
    posts = db.query(models.PostModel).filter(models.PostModel.user_id == current_user.id).all()
    
    return posts

@router.get("/getPost")
async def get_post(
    id: int = None,
    name: str = None,
    text: str = None,
    db=fastapi.Depends(get_db),
    current_user: User = fastapi.Depends(auth_service.get_current_user)):
    
    cashed_post = get_cached_post(id)
    if cashed_post:
        return cashed_post
    
    post = db.query(models.PostModel).filter(models.PostModel.user_id == current_user.id)
    
    if id is not None:
        post = post.filter(models.PostModel.id == id)
    if name:
        post = post.filter(models.PostModel.name == name)
    if text:
        post = post.filter(models.PostModel.text == text)
    
    post = post.first()
    if post:
        cache_post(current_user.id, post, expiration_time)  
    else:
        return {"error": "Post not found"}
        
    return post



@router.post("/")
async def addPost(post: schemas.PostRequestSchema, db = fastapi.Depends(get_db), current_user: User = fastapi.Depends(auth_service.get_current_user)):
    if len(post.text) > 1000:
        raise HTTPException(status_code=400, detail="Text field is too long")
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