import json
from pathlib import Path

import pytest

from bookmarks_converter.models import DBBookmark, Folder, Url, create_engine, sessionmaker

TEST_ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_ROOT_DIR.joinpath("resources")

TEST_FILE_FIREFOX_JSON = DATA_DIR.joinpath("bookmarks_firefox.json")
TEST_FILE_FIREFOX_HTML = DATA_DIR.joinpath("bookmarks_firefox.html")
TEST_FILE_FIREFOX_HTML_UNINDENTED = DATA_DIR.joinpath("bookmarks_firefox_unindented.html")
TEST_FILE_FIREFOX_HTML_FORMATTED = DATA_DIR.joinpath("bookmarks_firefox_formatted.html")
TEST_FILE_CHROME_JSON = DATA_DIR.joinpath("bookmarks_chrome.json")
TEST_FILE_CHROME_HTML = DATA_DIR.joinpath("bookmarks_chrome.html")


@pytest.fixture
def get_data_from_db():
    def _function(db_path, source):
        database_path = "sqlite:///" + str(db_path)
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        bookmarks = session.query(DBBookmark).order_by(DBBookmark.id).all()
        if source != None:
            root_date = session.query(DBBookmark).filter_by(title="root").one().date_added
        if source == "Chrome":
            folder_date = (
                session.query(DBBookmark).filter_by(title="Other Bookmarks").one().date_added
            )
        elif source == "Firefox":
            folder_date = (
                session.query(DBBookmark).filter_by(title="Bookmarks Menu").one().date_added
            )
        else:
            root_date = folder_date = None
        session.close()
        engine.dispose()
        return bookmarks, root_date, folder_date

    return _function


@pytest.fixture
def read_json():
    def _function(filepath) -> dict:
        with open(filepath, "r", encoding="Utf-8") as file_:
            jsondata = json.load(file_)
        return jsondata

    return _function


@pytest.fixture
def url_custom():
    return {
        "type": "url",
        "id": 2,
        "index": 0,
        "url": "https://www.google.com",
        "title": "Google",
        "date_added": 0,
        "icon": None,
        "iconuri": "https://www.google.com/favicon.ico",
        "tags": None,
    }


@pytest.fixture
def folder_custom():
    return {
        "type": "folder",
        "id": 1,
        "index": 0,
        "title": "Main Folder",
        "date_added": 0,
        "children": [],
    }


@pytest.fixture(scope="function")
def modify_folder_and_url_methods():
    """
    Because the guids for HTML parsed bookmarks are generated on the spot, the equality check will
    always fail. To overcome this we temporarily modify the equality method `__eq__` to ignore the
    guids.
    """

    def equality_ignore_guid(self, other) -> bool:
        for key in vars(self).keys():
            if key == "guid" or key.startswith("_"):
                continue
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    Folder.__eq__ = equality_ignore_guid
    Url.__eq__ = equality_ignore_guid
