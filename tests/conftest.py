import json
from pathlib import Path

import pytest
from bookmarks_converter.models import Bookmark, create_engine, sessionmaker

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR.joinpath("data")


@pytest.fixture
def source_bookmark_files():
    files = {str(x.name): str(x) for x in DATA_DIR.glob("bookmarks_*")}
    return files


@pytest.fixture
def result_bookmark_files():
    files = {str(x.name): str(x) for x in DATA_DIR.glob("from_*")}
    return files


@pytest.fixture
def get_data_from_db():
    def _function(db_path, source):
        database_path = "sqlite:///" + str(db_path)
        engine = create_engine(database_path, encoding="utf-8")
        Session = sessionmaker(bind=engine)
        session = Session()
        bookmarks = session.query(Bookmark).order_by(Bookmark.id).all()
        if source != None:
            root_date = session.query(Bookmark).filter_by(title="root").one().date_added
        if source == "Chrome":
            folder_date = (
                session.query(Bookmark)
                .filter_by(title="Other Bookmarks")
                .one()
                .date_added
            )
        elif source == "Firefox":
            folder_date = (
                session.query(Bookmark)
                .filter_by(title="Bookmarks Menu")
                .one()
                .date_added
            )
        else:
            root_date = folder_date = None
        session.close()
        return bookmarks, root_date, folder_date

    return _function


@pytest.fixture
def create_class_instance():
    def _function(data, class_):
        instance = class_()
        for key, value in data.items():
            if key == "iconuri":
                key = "icon_uri"
            setattr(instance, key, value)
        return instance

    return _function


@pytest.fixture
def read_json():
    def _function(filepath):
        with open(filepath, "r", encoding="Utf-8") as file_:
            jsondata = json.load(file_)
        return jsondata

    return _function


@pytest.fixture
def url_chrome():
    return {
        "date_added": "13244224395000000",
        "id": "1",
        "name": "Google",
        "type": "url",
        "url": "https://www.google.com",
    }


@pytest.fixture
def folder_chrome():
    return {
        "children": [],
        "date_added": "13244233436520764",
        "date_modified": "0",
        "id": "2",
        "name": "Main Folder",
        "type": "folder",
    }


@pytest.fixture
def url_firefox():
    return {
        "guid": "7TpRGhofxKDv",
        "title": "Google",
        "index": 0,
        "dateAdded": 1599750431776000,
        "lastModified": 1599750431776000,
        "id": 2,
        "typeCode": 1,
        "iconuri": "https://www.google.com/favicon.ico",
        "type": "text/x-moz-place",
        "uri": "https://www.google.com",
    }


@pytest.fixture
def folder_firefox():
    return {
        "guid": "K3LUb7o0kSUt",
        "title": "Main Folder",
        "index": 0,
        "dateAdded": 1599750431776000,
        "lastModified": 1599750431776000,
        "id": 1,
        "typeCode": 2,
        "type": "text/x-moz-place-container",
        "children": [],
    }


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
