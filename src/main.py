from fastapi import FastAPI
from src.routes import users_router, posts_router
import uvicorn

app = FastAPI(
    title="yaballe blogposts",
    description=" This is the API for the blogposts of Yabalee",
    version="1.0.0"
)

# Include routers
app.include_router(users_router)
app.include_router(posts_router)

@app.get("/")
def root():
    return {"message": "Welcome to the Blog API!"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
