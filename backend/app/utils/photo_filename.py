import datetime
import uuid
import zoneinfo
from pathlib import Path

from app.core.config import settings

FORMAT = "%Y%m%d"
TARGET_DIR = "photo"
PHOTO_EXT = ".jpg"


def generate_unique_filename() -> str:
    """Генерирует уникальное имя файла, сохраняя расширение."""
    local_tz = zoneinfo.ZoneInfo(settings.timezone)
    local_now = datetime.datetime.now(tz=local_tz)
    date_part = local_now.strftime(format=FORMAT)
    uuid_part = uuid.uuid4().hex
    ext_part = PHOTO_EXT
    return f"{date_part}_{uuid_part}{ext_part}"


def get_photo_path(unique_filename: str) -> tuple[Path, str]:
    """Возвращает абсолютный путь для сохранения и относительный для БД."""
    absolute_path = settings.media_root / TARGET_DIR
    absolute_path.mkdir(parents=True, exist_ok=True)
    relative_path = f"{TARGET_DIR}/{unique_filename}"
    return absolute_path / unique_filename, relative_path
