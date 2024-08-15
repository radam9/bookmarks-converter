from uuid import uuid4

import pytest
from conftest import TEST_FILE_CHROME_HTML, TEST_FILE_CHROME_JSON
from resources.bookmarks_chrome import bookmarks_as_json, bookmarks_html, bookmarks_json

from bookmarks_converter.converters.chrome import (
    CHROME_BOOKMARK_BAR_FOLDER_TITLE,
    CHROME_BOOKMARK_OTHER_FOLDER_TITLE,
    Chrome,
)
from bookmarks_converter.models import Folder, HTMLBookmark, SpecialFolder, Url


class TestChrome:
    chrome = Chrome()

    def test_as_html(self):
        result = self.chrome.as_html(bookmarks_html(merge_mobile_to_others=True, include_menu=True))

        with open(TEST_FILE_CHROME_HTML, "r") as f:
            expected = f.read()

        assert result == expected

    test_folder_as_html_params = (
        pytest.param(
            "some title",
            1719774198044000,
            None,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198">some title</H3>\n',
            id="normal_folder",
        ),
        pytest.param(
            "some title",
            0,
            None,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="0">some title</H3>\n',
            id="normal_folder_no_modified_date",
        ),
        pytest.param(
            "some & title < multiple > parts",
            0,
            None,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="0">some &amp; title &lt; multiple &gt; parts</H3>\n',
            id="normal_folder_html_escape_title",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            SpecialFolder.ROOT,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198">some title</H3>\n',
            id="special_folder_root",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            SpecialFolder.TOOLBAR,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198" PERSONAL_TOOLBAR_FOLDER="true">Bookmarks bar</H3>\n',
            id="special_folder_toolbar",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            SpecialFolder.OTHER,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198">some title</H3>\n',
            id="special_folder_other",
        ),
    )

    @pytest.mark.parametrize(
        "title,date_modified,special_folder,expected_result", test_folder_as_html_params
    )
    def test_folder_as_html(
        self, title: str, date_modified: int, special_folder: SpecialFolder, expected_result: str
    ):
        input_folder = Folder(
            guid=str(uuid4()),
            title=title,
            index=0,
            date_added=1659184459926000,
            date_modified=date_modified,
            id=1,
            special_folder=special_folder,
            children=[],
        )
        result = self.chrome._folder_as_html(input_folder)
        assert result == expected_result

    test_url_as_html_params = (
        pytest.param(
            "some title",
            1719774198044000,
            "https://www.example.com/apple-touch-icon.png",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==">some title</A>\n',
            id="url_full",
        ),
        pytest.param(
            "some title",
            0,
            "",
            "",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198">some title</A>\n',
            id="url_minimal",
        ),
        pytest.param(
            "some & title < multiple > parts",
            0,
            "",
            "",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198">some &amp; title &lt; multiple &gt; parts</A>\n',
            id="url_html_escape_title",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            "https://www.example.com/apple-touch-icon.png",
            "",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198">some title</A>\n',
            id="uri_no_icon",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            "",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==">some title</A>\n',
            id="uri_no_icon_uri",
        ),
        pytest.param(
            "some title",
            0,
            "https://www.example.com/apple-touch-icon.png",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==">some title</A>\n',
            id="uri_no_date_modified",
        ),
    )

    @pytest.mark.parametrize(
        "title,date_modified,icon_uri,icon,expected_result", test_url_as_html_params
    )
    def test_url_as_html(
        self, title: str, date_modified: int, icon_uri: str, icon: str, expected_result: str
    ):
        input_url = Url(
            guid=str(uuid4()),
            title=title,
            index=2,
            date_added=1719774198044000,
            date_modified=date_modified,
            id=45,
            url="https://www.example.com/",
            icon_uri=icon_uri,
            icon=icon,
        )

        result = self.chrome._url_as_html(input_url)
        assert result == expected_result

    def test_from_html(self, modify_folder_and_url_methods):
        result = self.chrome.from_html(TEST_FILE_CHROME_HTML)

        expected = bookmarks_html(merge_mobile_to_others=True)

        # the root and "other bookmarks" folder have the time generated during parsing, so we make them equal.
        expected.date_added = result.date_added
        expected.children[1].date_added = result.children[1].date_added

        assert result == expected

    test_get_html_special_folder_params = (
        pytest.param("test-title", None, {}, id="normal_folder"),
        pytest.param(
            CHROME_BOOKMARK_OTHER_FOLDER_TITLE, SpecialFolder.OTHER, {}, id="other_folder"
        ),
        pytest.param(
            CHROME_BOOKMARK_BAR_FOLDER_TITLE, SpecialFolder.TOOLBAR, {}, id="toolbar_folder"
        ),
        pytest.param(
            "test-title",
            SpecialFolder.TOOLBAR,
            {"personal_toolbar_folder": True},
            id="toolbar_folder_attr",
        ),
    )

    @pytest.mark.parametrize("title,special_folder,attrs", test_get_html_special_folder_params)
    def test_get_html_special_folder(self, title: str, special_folder: SpecialFolder, attrs: dict):
        input_attrs = {"title": title, **attrs}
        input_folder = HTMLBookmark(attrs=input_attrs, name="folder")
        result = self.chrome._get_html_special_folder(input_folder)
        assert result == special_folder

    def test_as_json(self, read_json):
        result = self.chrome.as_json(bookmarks_as_json())

        expected = read_json(TEST_FILE_CHROME_JSON)
        expected.pop("checksum")

        assert result == expected

    def test_folder_as_json(self):
        input_folder = Folder(
            guid="c4d6c7cd-5228-4d45-9317-7913b134ba38",
            title="test-title",
            index=0,
            date_added=1659184459926000,
            date_modified=1659184459926000,
            id=1,
            special_folder=SpecialFolder.ROOT,
            children=[],
        )

        expected_result = {
            "children": [],
            "date_added": "13303658059926000",
            "guid": "c4d6c7cd-5228-4d45-9317-7913b134ba38",
            "date_last_used": "0",
            "id": "1",
            "date_modified": "13303658059926000",
            "name": "test-title",
            "type": "folder",
        }

        result = self.chrome._folder_as_json(input_folder)
        assert result == expected_result

    def test_url_as_json(self):
        input_url = Url(
            guid="a8b6cce8-7bee-4840-ad9a-7c4684054e57",
            title="test-title",
            index=2,
            date_added=1719774198044000,
            date_modified=1719774198044000,
            id=45,
            url="https://www.example.com/",
            icon_uri="https://www.example.com/apple-touch-icon.png",
            icon="dummy-icon",
        )

        expected_result = {
            "date_added": "13364247798044000",
            "guid": "a8b6cce8-7bee-4840-ad9a-7c4684054e57",
            "id": "45",
            "date_last_used": "0",
            "name": "test-title",
            "type": "url",
            "url": "https://www.example.com/",
        }

        result = self.chrome._url_as_json(input_url)
        assert result == expected_result

    test_json_to_object_folder_params = (
        pytest.param(None, {}, id="normal_folder"),
        pytest.param(
            None,
            {"last_visited_desktop": "13204332604026373", "power_bookmark_meta": ""},
            id="meta_info",
        ),
        pytest.param(
            SpecialFolder.ROOT, {"id": 0, "name": "root", "other": None}, id="root_folder"
        ),
        pytest.param(SpecialFolder.TOOLBAR, {"name": "Bookmarks bar"}, id="toolbal_folder"),
        pytest.param(SpecialFolder.OTHER, {"name": "Other bookmarks"}, id="other_folder"),
        pytest.param(SpecialFolder.MOBILE, {"name": "Mobile bookmarks"}, id="mobile_folder"),
    )

    def test_from_json(self):
        result = self.chrome.from_json(TEST_FILE_CHROME_JSON)

        expected = bookmarks_json()

        # since the root folder is created and doesn't exist, we need to copy over it's guid.
        result.guid = expected.guid

        assert result == expected

    @pytest.mark.parametrize("special_folder,changes", test_json_to_object_folder_params)
    def test_json_to_object_folder(self, special_folder: SpecialFolder, changes: dict):
        folder_ = {
            "children": [],
            "date_added": "13244233436520764",
            "date_modified": "0",
            "id": "2",
            "name": "Main Folder",
            "type": "folder",
            "meta_info": {},
            "unsynced_meta_info": {},
        }
        folder_.update(changes)

        id_ = int(folder_["id"])
        name = folder_["name"]
        folder = Chrome._json_to_object(folder_)
        assert isinstance(folder, Folder)
        assert isinstance(folder.children, list)
        assert isinstance(folder.date_added, int)
        assert isinstance(folder.date_modified, int)
        assert folder.id == id_
        assert folder.title == name
        assert folder.special_folder == special_folder

    test_json_to_object_url_params = (
        pytest.param({}, id="no_meta_info"),
        pytest.param(
            {"last_visited_desktop": "13204332604026373", "power_bookmark_meta": ""}, id="meta_info"
        ),
    )

    @pytest.mark.parametrize("meta_info", test_json_to_object_url_params)
    def test_json_to_object_url(self, meta_info: dict):
        url_ = {
            "date_added": "13244224395000000",
            "id": "1",
            "name": "test-title",
            "type": "url",
            "url": "https://www.example.com",
            "meta_info": meta_info,
            "unsynced_meta_info": {},
        }

        id_ = int(url_["id"])
        title = url_["name"]
        url_address = url_["url"]
        url = Chrome._json_to_object(url_)
        assert isinstance(url, Url)
        assert isinstance(url.date_added, int)
        assert isinstance(url.date_modified, int)
        assert url.id == id_
        assert url.title == title
        assert url.url == url_address
