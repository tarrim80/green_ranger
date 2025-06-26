from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PhotoBase(BaseModel):
    file_path: str


class PhotoCreate(PhotoBase):
    pass


class PhotoRead(PhotoBase):
    id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
