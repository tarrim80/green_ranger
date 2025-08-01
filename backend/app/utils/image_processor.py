from io import BytesIO

from PIL import Image

from app.core.constants import FORMAT_PHOTO, MAX_PHOTO_PX, PHOTO_QUALITY


def process_image(
    file_bytes: bytes,
) -> bytes:
    """Обрабатывает изображение: изменяет размер и оптимизирует."""
    input_stream = BytesIO(initial_bytes=file_bytes)
    image = Image.open(fp=input_stream)
    image.thumbnail(size=MAX_PHOTO_PX)
    output_stream = BytesIO()
    image.save(fp=output_stream, format=FORMAT_PHOTO, quality=PHOTO_QUALITY)
    return output_stream.getvalue()
