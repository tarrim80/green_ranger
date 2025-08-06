import os
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.exceptions import ExceptionDetails, FileProcessingError
from app.utils.image_processor import process_image
from app.utils.photo_filename import generate_unique_basename, get_photo_paths


async def save_uploaded_images(
    files: list[UploadFile],
) -> tuple[list[dict[str, str]], list[Path]]:
    """
    Сохраняет загруженные файлы изображений и их миниаюры на сервер
    после их обработки.
    """
    photos_data = []
    saved_file_paths = []
    try:
        for file in files:
            if not file.filename:
                continue
            unique_filenames = generate_unique_basename()
            (
                photo_full_path,
                photo_relative_path,
                thumb_full_path,
                thumb_relative_path,
            ) = get_photo_paths()
            content = await file.read()
            photo, thumbnail = process_image(file_bytes=content)
            async with aiofiles.open(file=photo_full_path, mode="wb") as f:
                await f.write(photo)
            async with aiofiles.open(file=thumb_full_path, mode="wb") as f:
                await f.write(thumbnail)

            saved_file_paths.append(photo_full_path)
            saved_file_paths.append(thumb_full_path)
            photos_data.append(
                {
                    "file_path": photo_relative_path,
                    "thumbnail_path": thumb_relative_path,
                }
            )
        return photos_data, saved_file_paths
    except Exception as e:
        for path in saved_file_paths:
            if os.path.exists(path):
                os.remove(path)
        raise FileProcessingError(
            f"{ExceptionDetails.FAILED_TO_PROCESSING_FILE}: \
                        {e}"
        )
