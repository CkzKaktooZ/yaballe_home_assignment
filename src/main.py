from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="yaballe blogposts",
    description=" This is the API for the blogposts of Yabalee",
    version="1.0.0"
)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
