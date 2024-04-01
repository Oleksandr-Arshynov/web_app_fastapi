from fastapi import FastAPI
import uvicorn


import src.auth.routes
import src.posts.routes

posts_api = FastAPI()

posts_api.include_router(src.auth.routes.router)
posts_api.include_router(src.posts.routes.router)




if __name__ == "__main__":
    uvicorn.run(
        "main:posts_api", host="0.0.0.0", port=8000, reload=True
    )