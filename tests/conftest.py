import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, with_polymorphic

from bookmarks_converter.models import DBBookmark, DBFolder, DBUrl, Folder, SpecialFolder, Url

TEST_ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = TEST_ROOT_DIR.joinpath("resources")

TEST_FILE_FIREFOX_JSON = DATA_DIR.joinpath("bookmarks_firefox.json")
TEST_FILE_FIREFOX_JSON_WITH_SEPARATOR = DATA_DIR.joinpath("bookmarks_firefox_with_separator.json")
TEST_FILE_FIREFOX_HTML = DATA_DIR.joinpath("bookmarks_firefox.html")
TEST_FILE_CHROME_JSON = DATA_DIR.joinpath("bookmarks_chrome.json")
TEST_FILE_CHROME_HTML = DATA_DIR.joinpath("bookmarks_chrome.html")
TEST_FILE_BOOKMARKIE_DB = DATA_DIR.joinpath("bookmarks_bookmarkie.db")
TEST_FILE_BOOKMARKIE_HTML = DATA_DIR.joinpath("bookmarks_bookmarkie.html")
TEST_FILE_BOOKMARKIE_JSON = DATA_DIR.joinpath("bookmarks_bookmarkie.json")
TEST_FILE_BOOKMARKIE_HTML_UNINDENTED = DATA_DIR.joinpath("bookmarks_bookmarkie_unindented.html")
TEST_FILE_BOOKMARKIE_HTML_FORMATTED = DATA_DIR.joinpath("bookmarks_bookmarkie_formatted.html")
TEST_INPUT_FILE = DATA_DIR.joinpath("INPUT_TEST_FILE")
TEST_OUTPUT_FILE = DATA_DIR.joinpath("OUTPUT_TEST_FILE")


@pytest.fixture
def get_data_from_db():
    def _function(db_path: Path) -> DBBookmark:
        database_path = "sqlite:///" + str(db_path)
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            bookmarks = session.query(with_polymorphic(DBBookmark, [DBFolder, DBUrl])).all()
            session.expunge_all()

        for bookmark in bookmarks:
            if (
                isinstance(bookmark, DBFolder)
                and bookmark.special_folder == SpecialFolder.ROOT.value
            ):
                return bookmark

    return _function


@pytest.fixture
def read_json():
    def _function(filepath: Path) -> dict:
        with filepath.open("r", encoding="utf-8") as file_:
            jsondata = json.load(file_)
        return jsondata

    return _function


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
