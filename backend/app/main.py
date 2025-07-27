from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.constants import SAFE_METHODS
from app.api.routers import main_router
from app.core.config import settings

app = FastAPI(title=settings.app_title)

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_title,
        version="1.0.0",
        description="API для системы регистрации болезней деревьев",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    api_prefix = main_router.prefix

    public_paths = {
        f"{api_prefix}/auth/jwt/login",
        f"{api_prefix}/auth/jwt/register",
    }

    protected_get_path_prefixes = {
        f"{api_prefix}/users/",
    }

    for path, path_item in openapi_schema.get("paths", {}).items():
        if path in public_paths:
            continue

        for method in path_item:
            is_protected_get = method.lower() == "get" and any(
                path.startswith(prefix)
                for prefix in protected_get_path_prefixes
            )

            is_dangerous_method = method.lower() not in SAFE_METHODS

            if is_dangerous_method or is_protected_get:
                path_item[method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
