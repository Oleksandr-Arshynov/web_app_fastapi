import datetime
import pydantic

from src.auth.schemas import UserDb

class PostResponseSchema(pydantic.BaseModel):
    id: int
    name: str
    text: str
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
    current_user: UserDb | None
    
    class Config:
        arbitrary_types_allowed = True
    
class PostRequestSchema(pydantic.BaseModel):
    name:str
    text: str
    
    class Config:
        arbitrary_types_allowed = True