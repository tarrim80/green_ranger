from io import BytesIO

from PIL import Image

from app.core.constants import (
    FORMAT_PHOTO,
    MAX_PHOTO_PX,
    PHOTO_QUALITY,
    THUMBNAIL_QUALITY,
    THUMBNAIL_SIZE,
)


def process_image(
    file_bytes: bytes,
) -> tuple[bytes, bytes]:
    """Обрабатывает изображение: изменяет размер и создает миниатюру."""
    image = Image.open(BytesIO(file_bytes))

    thumb_image = image.copy()
    thumb_image.thumbnail(THUMBNAIL_SIZE)
    thumb_stream = BytesIO()
    thumb_image.save(
        thumb_stream, format=FORMAT_PHOTO, quality=THUMBNAIL_QUALITY
    )

    image.thumbnail(MAX_PHOTO_PX)
    original_stream = BytesIO()
    image.save(original_stream, format=FORMAT_PHOTO, quality=PHOTO_QUALITY)

    return original_stream.getvalue(), thumb_stream.getvalue()
