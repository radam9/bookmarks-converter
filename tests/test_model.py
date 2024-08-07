import pytest

from bookmarks_converter.models import HTMLBookmark, DBBookmark, TYPE_FOLDER, TYPE_URL


class TestDBBookmark:
    def test_equality(self):
        instance_a = DBBookmark(
            id=1,
            title="some title",
            index=0,
            parent_id=None,
            date_added=9000,
            type="folder",
            children=[],
        )
        instance_b = DBBookmark(
            id=1,
            title="some title",
            index=0,
            parent_id=None,
            date_added=9000,
            type="folder",
            children=[],
        )

        assert instance_a == instance_b

    def test_equality_false(self):
        instance_a = DBBookmark()
        instance_b = DBBookmark(title="something else")
        assert instance_a != instance_b


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
        "icon": None,
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
