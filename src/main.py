from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from src.routes import UserRoutes, PostRoutes
from src.database import engine, Base
import uvicorn


app = FastAPI(
    title="Yaballe blogposts",
    description="This is the API for the blogposts of Yaballee",
    version="1.0.0",
)

app.include_router(UserRoutes)
app.include_router(PostRoutes)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My Blog API",
        version="1.0.0",
        description="A blogging platform with auth and voting",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    # Apply BearerAuth to all endpoints globally
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"message": "Welcome to the Blog API!"}


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
