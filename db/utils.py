from os import PathLike
from typing import Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def session_factory(file_path: PathLike) -> Callable:
    engine = create_async_engine(f"sqlite+aiosqlite:///{file_path}", echo=False)
    return async_sessionmaker(engine, expire_on_commit=False)
