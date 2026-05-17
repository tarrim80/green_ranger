from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.validators import validate_photo_links

PHOTO_FIELDS_CONFIG = {
    "id": [Field(description="Уникальный идентификатор", examples=[1, 2, 3])],
    "file_path": [
        Field(
            description="Путь хранения фото",
            examples=["media/photo/file_name.jpg"],
        )
    ],
    "thumbnail_path": [
        Field(
            description="Путь хранения миниатюры изображения",
            examples=["media/photo/file_name_thumb.jpg"],
        )
    ],
    "uploaded_at": [
        Field(
            description="Дата и время загрузки фото",
        )
    ],
    "defect_type_id": [
        Field(
            description="ID связанного вида дефекта",
            examples=[1],
        )
    ],
    "survey_id": [
        Field(
            description="ID связанного обследования",
            examples=[1],
        )
    ],
    "survey_defect_id": [
        Field(
            description="ID связанного конкретного дефекта",
            examples=[1],
        )
    ],
}


class PhotoBase(BaseModel):
    """Базовая схема для фотографии."""

    file_path: Annotated[str, *PHOTO_FIELDS_CONFIG["file_path"]]
    thumbnail_path: Annotated[str, *PHOTO_FIELDS_CONFIG["thumbnail_path"]]
    defect_type_id: Annotated[
        int | None, *PHOTO_FIELDS_CONFIG["defect_type_id"]
    ] = None
    survey_id: Annotated[int | None, *PHOTO_FIELDS_CONFIG["survey_id"]] = None
    survey_defect_id: Annotated[
        int | None, *PHOTO_FIELDS_CONFIG["survey_defect_id"]
    ] = None


class PhotoCreate(PhotoBase):
    """Схема для создания фотографии с валидацией связей."""

    @model_validator(mode="after")
    def check_links(self) -> "PhotoCreate":
        validate_photo_links(self.model_dump())
        return self


class PhotoUpdate(PhotoBase):
    """Схема для обновления фотографии."""

    file_path: Annotated[str, *PHOTO_FIELDS_CONFIG["file_path"]] | None = None  # type: ignore
    thumbnail_path: Annotated[str, *PHOTO_FIELDS_CONFIG["thumbnail_path"]] | None = None  # type: ignore


class PhotoRead(PhotoBase):
    """Схема для чтения фотографии."""

    id: Annotated[int, *PHOTO_FIELDS_CONFIG["id"]]
    uploaded_at: Annotated[datetime, *PHOTO_FIELDS_CONFIG["uploaded_at"]]

    model_config = ConfigDict(from_attributes=True)
