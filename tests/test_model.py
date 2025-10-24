import copy

import pytest

from bookmarks_converter.models import (
    TYPE_FOLDER,
    TYPE_URL,
    DBFolder,
    DBUrl,
    HTMLBookmark,
    SpecialFolder,
)


@pytest.fixture(scope="function")
def folder_db():
    child = DBFolder(
        _id=2,
        guid="9abdc1e1-4e5f-4069-bdc1-e14e5fc069fb",
        title="test folder",
        index=0,
        parent_id=None,
        date_added=9000,
        date_modified=7000,
        special_folder=SpecialFolder.ROOT,
    )
    child.children = [
        DBUrl(
            _id=3,
            guid="f4acff60-7500-4110-acff-607500511033",
            title="test url",
            index=0,
            parent_id=None,
            date_added=9000,
            date_modified=7000,
            url="https://www.example.com",
            icon="some icon data",
            icon_uri="https://www.exmaple.com/icon",
            tags=["tag1", "tag2"],
        )
    ]
    main = DBFolder(
        _id=1,
        guid="79854084-0957-4817-8540-840957881708",
        title="test folder",
        index=1,
        parent_id=None,
        date_added=9000,
        date_modified=7000,
        special_folder=SpecialFolder.ROOT,
    )
    main.children = [child]
    return main


@pytest.fixture(scope="function")
def url_db():
    return DBUrl(
        _id=1,
        guid="346301a9-7739-42a0-a301-a97739e2a03d",
        title="test url",
        index=2,
        parent_id=None,
        date_added=9000,
        date_modified=7000,
        url="https://www.example.com",
        icon="some icon data",
        icon_uri="https://www.exmaple.com/icon",
        tags=["tag1", "tag2"],
    )


class TestDBBookmark:
    def test_equality(self, folder_db):
        folder_db_new = copy.deepcopy(folder_db)
        assert folder_db == folder_db_new

    def test_equality_false(self, folder_db):
        folder_db_new = copy.deepcopy(folder_db)
        folder_db_new.title = "new title"
        assert folder_db != folder_db_new

    def test_type_folder(self):
        folder = DBFolder(title="", index=0, parent_id=None)
        assert folder.type == "folder"

    def test_type_url(self):
        url = DBUrl(index=0, parent_id=None, url="")
        assert url.type == "url"

    def test_url_no_title(self):
        url = DBUrl(index=0, parent_id=None, url="https://www.example.com")
        assert url.title == url.url


@pytest.fixture(scope="function")
def folder_attrs():
    return {
        "type": "folder",
        "id": 1,
        "index": 0,
        "title": "Main Folder",
        "add_date": 0,
        "last_modified": 0,
        "children": [],
    }


@pytest.fixture(scope="function")
def url_attrs():
    return {
        "type": "url",
        "id": 9000,
        "index": 0,
        "href": "https://www.example.com",
        "title": "Google",
        "add_date": 0,
        "last_modified": 0,
        "icon": "",
        "icon_uri": "https://www.example.com/icon",
        "tags": None,
    }


class TestHTMLBookmark:
    def test_folder_custom(self, folder_attrs):
        # f_attrs = folder_attrs
        folder = HTMLBookmark(name="h3", attrs=folder_attrs)
        assert folder_attrs.get("id") == folder.id
        assert folder_attrs.get("index") == folder.index
        assert folder_attrs.get("title") == folder.title
        assert folder_attrs.get("type") == folder.type
        assert TYPE_FOLDER == folder.type
        assert isinstance(folder.contents, list)
        assert isinstance(folder.children, list)
        assert len(folder.children) == 0

    def test_url_custom(self, url_attrs):
        url = HTMLBookmark(name="a", attrs=url_attrs)
        assert url_attrs.get("icon") == url.icon
        assert url_attrs.get("icon_uri") == url.icon_uri
        assert url_attrs.get("id") == url.id
        assert url_attrs.get("index") == url.index
        assert url_attrs.get("title") == url.title
        assert url_attrs.get("type") == url.type
        assert TYPE_URL == url.type
        assert url_attrs.get("href") == url.url

    def test_date_added(self, folder_attrs, url_attrs):
        time_ = 1000
        expected_time = time_ * 1000_000
        folder_attrs["add_date"] = time_
        folder = HTMLBookmark(name="h3", attrs=folder_attrs)
        assert expected_time == folder.date_added

        url_attrs["add_date"] = time_
        url = HTMLBookmark(name="a", attrs=url_attrs)
        assert expected_time == url.date_added

    def test_date_modified(self, folder_attrs, url_attrs):
        time_ = 9999
        expected_time = time_ * 1000_000
        folder_attrs["last_modified"] = time_
        folder = HTMLBookmark(name="h3", attrs=folder_attrs)
        assert expected_time == folder.date_modified

        url_attrs["last_modified"] = time_
        url = HTMLBookmark(name="a", attrs=url_attrs)
        assert expected_time == url.date_modified

    def test_id_setter(self, folder_attrs, url_attrs):
        new_id = 9009

        folder = HTMLBookmark(name="h3", attrs=folder_attrs)
        assert folder_attrs.get("id") == folder.id
        folder.id = new_id
        assert new_id == folder.id

        url = HTMLBookmark(name="a", attrs=url_attrs)
        assert url_attrs.get("id") == url.id
        url.id = new_id
        assert new_id == url.id

    def test_title_setter(self, folder_attrs, url_attrs):
        new_title = "New Title"

        folder = HTMLBookmark(name="h3", attrs=folder_attrs)
        assert folder_attrs.get("title") == folder.title
        folder.title = new_title
        assert new_title == folder.title

        url = HTMLBookmark(name="a", attrs=url_attrs)
        assert url_attrs.get("title") == url.title
        url.title = new_title
        assert new_title == url.title

    def test_type(self, folder_attrs, url_attrs):
        folder = HTMLBookmark(name="h3", attrs=folder_attrs)
        assert folder.type == TYPE_FOLDER
        url = HTMLBookmark(name="a", attrs=url_attrs)
        assert url.type == TYPE_URL
