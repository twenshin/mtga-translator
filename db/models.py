from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая модель"""


class LocalizationModel(Base):
    __tablename__ = "Loc"

    Key: Mapped[str] = mapped_column(primary_key=True)
    Bundle: Mapped[str]
    enUS: Mapped[str]
    ptBR: Mapped[str]
    frFR: Mapped[str]
    itIT: Mapped[str]
    deDe: Mapped[str]
    esES: Mapped[str]
    jaJP: Mapped[str]
    koKR: Mapped[str]
