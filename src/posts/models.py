import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(30), unique=True)
    hash_password = sa.Column(sa.String)
    refresh_token = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
class PostModel(Base):
    __tablename__ = "posts"
    
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))
    text = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    user = orm.relationship("User", backref="posts", lazy="joined")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "user_id": self.user_id
        }
    
class CachedData(Base):
    __tablename__ = "cached_data"
    
    id = sa.Column(sa.Integer, primary_key=True)
    query_id = sa.Column(sa.String)
    query_result = sa.Column(sa.String)
    expiration_time = sa.Column(sa.DateTime)
    