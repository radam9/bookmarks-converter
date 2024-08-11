"""Bookmarks Converter, is a package that converts the webpage bookmarks
from DB/HTML/JSON to DB/HTML/JSON.

The DB files supported are custom (self made) sqlite database files,
to see the exact format of the database you can check the .db file found
in the data folder.

The HTML files supported are Netscape-Bookmark files from either Chrome or
Firefox. The output HTML files adhere to the firefox format.

The JSON files supported are the Chrome bookmarks file, the Firefox
.json bookmarks export file, and the custom json file created by this package"""


import json
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .converters.chrome import Chrome
from .converters.firefox import Firefox
from .models import Base, DBBookmark


class BookmarksConverter:
    """Bookmarks Converter class that converts the bookmarks to DB/HTML/JSON.

    Usage:
    1- Instantiate a class and pass in the filepath as string or `Path` object:
        - `instance = BookmarksConverter(filepath)`.
    2- Import and Parse the bookmarks file passing the source format as a string in lower case:
        - `instance.parse("db")`, for a database file.
        - `instance.parse("html")`, for a html file.
        - `instance.parse("json")`, for a json file.
    3- Convert the data to the desired format passing the format as a lower
    case string:
        - `instance.convert("db")`, convert to database.
        - `instance.convert("html")`, convert to html.
        - `instance.convert("json")`, convert to json.
    4- At this point the bookmarks are stored in the `bookmarks` attribute
        accessible through `instance.bookmarks`.
    5- Export the bookmarks to a file using the save method `instance.save()`.
    """

    Chrome = Chrome()
    Firefox = Firefox()

    @staticmethod
    def save_html(bookmarks: str, filepath: Optional[Path] = None):
        """Export the bookmarks as HTML."""
        if filepath is None:
            filepath = Path()
        with open(filepath, "w", encoding="utf-8") as file_:
            file_.write(bookmarks)

    @staticmethod
    def save_json(bookmarks: dict, filepath: Optional[Path] = None):
        """Function to export the bookmarks as JSON."""
        if filepath is None:
            filepath = Path()
        with open(filepath, "w", encoding="utf-8") as file_:
            json.dump(bookmarks, file_, ensure_ascii=False)

    @staticmethod
    def save_db(bookmarks: DBBookmark, filepath: Optional[Path] = None):
        """Function to export the bookmarks as SQLite3 DB."""
        if filepath is None:
            filepath = Path()
        database_path = f"sqlite:///{str(filepath)}"
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.commit()
        session.bulk_save_objects(bookmarks)
        session.commit()
        session.close()
        engine.dispose()
