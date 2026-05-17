from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    NotAllowedError,
    NotFoundError,
    PermissionDenniedError,
)


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Базовый обработчик для всех исключений приложения."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def not_found_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик исключения NotFoundError (404)."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def permission_denied_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Обработчик исключения PermissionDenniedError (403)."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


async def not_allowed_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Обработчик исключения NotAllowedError (405)."""
    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={"detail": str(exc)},
    )


async def value_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик стандартного ValueError (400) для бизнес-валидаций."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики исключений в приложении FastAPI."""
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(PermissionDenniedError, permission_denied_error_handler)
    app.add_exception_handler(NotAllowedError, not_allowed_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(AppException, app_exception_handler)
