from app.api.routers import main_router
from app.core.config import settings
from fastapi import FastAPI

app = FastAPI(title=settings.app_title)

app.include_router(main_router)


@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}
