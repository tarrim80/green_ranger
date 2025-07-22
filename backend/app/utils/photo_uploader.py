import os

import aiofiles
from fastapi import UploadFile

from app.core.exceptions import ExceptionDetails, FileProcessingError
from app.utils.image_processor import process_image
from app.utils.photo_filename import generate_unique_filename, get_photo_path


async def save_uploaded_images(
    files: list[UploadFile],
) -> tuple[list[dict], list[str]]:
    photos_data = []
    saved_file_paths = []

    try:
        for file in files:
            if not file.filename:
                continue
            unique_filename = generate_unique_filename()
            full_path, relative_path = get_photo_path(
                unique_filename=unique_filename
            )
            try:
                content = await file.read()
                resize_photo = process_image(file_bytes=content)
                async with aiofiles.open(file=full_path, mode="wb") as f:
                    await f.write(resize_photo)
            except Exception as e:
                raise FileProcessingError(
                    f"{ExceptionDetails.FAILED_TO_PROCESSING_FILE}: \
                        {file.filename} - {e}"
                )
            saved_file_paths.append(full_path)
            photos_data.append({"file_path": relative_path})

        return photos_data, saved_file_paths

    except FileProcessingError as e:
        for filename in saved_file_paths:
            os.remove(filename)
        raise e
