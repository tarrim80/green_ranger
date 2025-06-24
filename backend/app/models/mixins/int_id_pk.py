from sqlalchemy.orm import Mapped, mapped_column


class IntIdPkMixin:
    """Первичный ключ Integer."""

    id: Mapped[int] = mapped_column(primary_key=True)
