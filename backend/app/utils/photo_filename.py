import datetime
import uuid
import zoneinfo
from pathlib import Path

from app.core.config import settings

FORMAT = "%Y%m%d"
TARGET_DIR = "photo"
THUMBNAIL_TARGET_DIR = "thumbnails"
THUMBNAIL_SUFFIX = "thumb"
PHOTO_EXT = ".jpg"


def generate_unique_basename() -> str:
    """
    Генерирует основу уникальных имен для файла изображения и его миниатюры.
    """
    local_tz = zoneinfo.ZoneInfo(settings.timezone)
    local_now = datetime.datetime.now(tz=local_tz)
    date_part = local_now.strftime(format=FORMAT)
    uuid_part = uuid.uuid4().hex
    return f"{date_part}_{uuid_part}"


def get_photo_paths() -> tuple[Path, str, Path, str]:
    """
    Формирует абсолютные и относительные пути для сохранения фото и миниатюры.
    """
    basename = generate_unique_basename()

    photo_filename = f"{basename}{PHOTO_EXT}"
    thumb_filename = f"{basename}_{THUMBNAIL_SUFFIX}{PHOTO_EXT}"

    absolute_dir = settings.media_root / TARGET_DIR
    absolute_dir.mkdir(parents=True, exist_ok=True)

    full_photo_path = absolute_dir / photo_filename
    relative_photo_path = f"{TARGET_DIR}/{photo_filename}"

    full_thumb_path = absolute_dir / thumb_filename
    relative_thumb_path = f"{TARGET_DIR}/{thumb_filename}"

    return (
        full_photo_path,
        relative_photo_path,
        full_thumb_path,
        relative_thumb_path,
    )
