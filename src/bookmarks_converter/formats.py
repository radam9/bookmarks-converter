import json
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bookmarks_converter.converters.converter import Converter
from bookmarks_converter.models import Base, Bookmark, DBBookmark


class Format(StrEnum):
    DB = "db"
    HTML = "html"
    JSON = "json"

    def __repr__(self) -> str:
        return f"'{self.value}'"

    def __str__(self) -> str:
        return self.value


class BaseFormat:
    def __init__(self, extension: Format):
        self.extension = extension

    def load(self, converter: Converter, path: Path) -> Bookmark:
        raise NotImplementedError

    def save(self, converter: Converter, bookmarks: Bookmark, path: Path):
        raise NotImplementedError


class DBFormat(BaseFormat):
    def load(self, converter: Converter, path: Path) -> Bookmark:
        return converter.from_db(path)

    def save(self, converter: Converter, bookmarks: Bookmark, path: Path):
        result = converter.as_db(bookmarks)
        save_db(result, path)


class HTMLFormat(BaseFormat):
    def load(self, converter: Converter, path: Path) -> Bookmark:
        return converter.from_html(path)

    def save(self, converter: Converter, bookmarks: Bookmark, path: Path):
        result = converter.as_html(bookmarks)
        save_html(result, path)


class JSONFormat(BaseFormat):
    def load(self, converter: Converter, path: Path) -> Bookmark:
        return converter.from_json(path)

    def save(self, converter: Converter, bookmarks: Bookmark, path: Path):
        result = converter.as_json(bookmarks)
        save_json(result, path)


FORMATS = {
    Format.DB: DBFormat(Format.DB),
    Format.HTML: HTMLFormat(Format.HTML),
    Format.JSON: JSONFormat(Format.JSON),
}


def _new_file_name(path: Path, extension: Format) -> Path:
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.joinpath(f"bookmarks-{now}.{extension}")


def _ensure_path_exists(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def save_db(bookmarks: DBBookmark, filepath: Path):
    """Function to export the bookmarks as SQLite3 DB.
    This function does not save bookmarks to an already existing database, but rather creates
    a new database."""
    _ensure_path_exists(filepath)
    database_path = "sqlite:///" + str(filepath)
    engine = create_engine(database_path)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        Base.metadata.create_all(engine)
        session.commit()
        session.add(bookmarks)
        session.commit()


def save_html(bookmarks: str, filepath: Optional[Path] = None):
    """Export the bookmarks as HTML."""
    _ensure_path_exists(filepath)
    with filepath.open("w", encoding="utf-8") as file:
        file.write(bookmarks)


def save_json(bookmarks: dict, filepath: Path):
    """Function to export the bookmarks as JSON."""
    _ensure_path_exists(filepath)
    with filepath.open("w", encoding="utf-8") as file:
        json.dump(bookmarks, file, ensure_ascii=False, indent=2)
