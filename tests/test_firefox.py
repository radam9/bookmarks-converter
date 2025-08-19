from pathlib import Path
from uuid import uuid4

import pytest
from conftest import (
    TEST_FILE_FIREFOX_HTML,
    TEST_FILE_FIREFOX_JSON,
    TEST_FILE_FIREFOX_JSON_WITH_SEPARATOR,
)
from resources.bookmarks_firefox import bookmarks_html, bookmarks_json

from bookmarks_converter.converters.firefox import (
    MOZILLA_CONTAINER_CONST,
    MOZILLA_GUID_LENGTH,
    MOZILLA_MENU_FOLDER_HTML_TITLE,
    MOZILLA_MENU_FOLDER_JSON_GUID,
    MOZILLA_MENU_FOLDER_JSON_TITLE,
    MOZILLA_MOBILE_FOLDER_JSON_GUID,
    MOZILLA_MOBILE_FOLDER_JSON_TITLE,
    MOZILLA_OTHER_FOLDER_HTML_TITLE,
    MOZILLA_OTHER_FOLDER_JSON_GUID,
    MOZILLA_OTHER_FOLDER_JSON_TITLE,
    MOZILLA_PLACE_CONST,
    MOZILLA_ROOT_FOLDER_JSON_GUID,
    MOZILLA_ROOT_FOLDER_JSON_TITLE,
    MOZILLA_TOOLBAR_FOLDER_HTML_TITLE,
    MOZILLA_TOOLBAR_FOLDER_JSON_GUID,
    MOZILLA_TOOLBAR_FOLDER_JSON_TITLE,
    Firefox,
)
from bookmarks_converter.models import Folder, HTMLBookmark, SpecialFolder, Url


class TestFirefox:
    firefox = Firefox()

    def test_as_html(self):
        result = self.firefox.as_html(bookmarks_html(include_mobile=True))

        with TEST_FILE_FIREFOX_HTML.open("r", encoding="utf-8") as f:
            expected = f.read()

        assert result == expected

    test_get_html_special_folder_params = (
        pytest.param("test-title", None, id="normal_folder"),
        pytest.param(MOZILLA_MENU_FOLDER_HTML_TITLE, SpecialFolder.MENU, id="menu_folder"),
        pytest.param(MOZILLA_TOOLBAR_FOLDER_HTML_TITLE, SpecialFolder.TOOLBAR, id="toolbar_folder"),
        pytest.param(MOZILLA_OTHER_FOLDER_HTML_TITLE, SpecialFolder.OTHER, id="other_folder"),
    )

    @pytest.mark.parametrize("title,special_folder", test_get_html_special_folder_params)
    def test_get_html_special_folder(self, title: str, special_folder: SpecialFolder):
        input_folder = HTMLBookmark(attrs={"title": title}, name="folder")
        result = self.firefox._get_html_special_folder(input_folder)
        assert result == special_folder

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
            '<DT><H3 ADD_DATE="1659184459">some title</H3>\n',
            id="normal_folder_no_modified_date",
        ),
        pytest.param(
            "some & title < multiple > parts",
            0,
            None,
            '<DT><H3 ADD_DATE="1659184459">some &amp; title &lt; multiple &gt; parts</H3>\n',
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
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198" PERSONAL_TOOLBAR_FOLDER="true">Bookmarks Toolbar</H3>\n',
            id="special_folder_toolbar",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            SpecialFolder.OTHER,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198" UNFILED_BOOKMARKS_FOLDER="true">Other Bookmarks</H3>\n',
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
        result = self.firefox._folder_as_html(input_folder)
        assert result == expected_result

    test_url_as_html_params = (
        pytest.param(
            "some title",
            1719774198044000,
            "https://www.example.com/apple-touch-icon.png",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" LAST_MODIFIED="1719774198" ICON_URI="https://www.example.com/apple-touch-icon.png" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==">some title</A>\n',
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
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" LAST_MODIFIED="1719774198" ICON_URI="https://www.example.com/apple-touch-icon.png">some title</A>\n',
            id="uri_no_icon",
        ),
        pytest.param(
            "some title",
            1719774198044000,
            "",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" LAST_MODIFIED="1719774198" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==">some title</A>\n',
            id="uri_no_icon_uri",
        ),
        pytest.param(
            "some title",
            0,
            "https://www.example.com/apple-touch-icon.png",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==",
            '<DT><A HREF="https://www.example.com/" ADD_DATE="1719774198" ICON_URI="https://www.example.com/apple-touch-icon.png" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAA==">some title</A>\n',
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

        result = self.firefox._url_as_html(input_url)
        assert result == expected_result

    def test_from_html(self, modify_folder_and_url_methods):
        result = self.firefox.from_html(TEST_FILE_FIREFOX_HTML)

        expected = bookmarks_html(include_mobile=False)

        # the root and menu folder have the time generated during parsing, so we make them equal.
        expected.date_added = result.date_added
        expected.children[0].date_added = result.children[0].date_added

        assert result == expected

    def test_as_json(self, read_json):
        result = self.firefox.as_json(bookmarks_json())

        expected = read_json(TEST_FILE_FIREFOX_JSON)

        assert result == expected

    test_folder_as_json = (
        pytest.param(
            1719774198044000,
            None,
            {"title": "test-title"},
            id="normal_folder",
        ),
        pytest.param(
            0,
            None,
            {"lastModified": 0, "title": "test-title"},
            id="normal_folder_no_modified_date",
        ),
        pytest.param(
            1719774198044000,
            SpecialFolder.ROOT,
            {
                "title": MOZILLA_ROOT_FOLDER_JSON_TITLE,
                "root": "placesRoot",
                "guid": MOZILLA_ROOT_FOLDER_JSON_GUID,
            },
            id="special_folder_root",
        ),
        pytest.param(
            1719774198044000,
            SpecialFolder.MENU,
            {
                "title": MOZILLA_MENU_FOLDER_JSON_TITLE,
                "root": "bookmarksMenuFolder",
                "guid": MOZILLA_MENU_FOLDER_JSON_GUID,
            },
            id="special_folder_menu",
        ),
        pytest.param(
            1719774198044000,
            SpecialFolder.TOOLBAR,
            {
                "title": MOZILLA_TOOLBAR_FOLDER_JSON_TITLE,
                "root": "toolbarFolder",
                "guid": MOZILLA_TOOLBAR_FOLDER_JSON_GUID,
            },
            id="special_folder_toolbar",
        ),
        pytest.param(
            1719774198044000,
            SpecialFolder.OTHER,
            {
                "title": MOZILLA_OTHER_FOLDER_JSON_TITLE,
                "root": "unfiledBookmarksFolder",
                "guid": MOZILLA_OTHER_FOLDER_JSON_GUID,
            },
            id="special_folder_other",
        ),
        pytest.param(
            1719774198044000,
            SpecialFolder.MOBILE,
            {
                "title": MOZILLA_MOBILE_FOLDER_JSON_TITLE,
                "root": "mobileFolder",
                "guid": MOZILLA_MOBILE_FOLDER_JSON_GUID,
            },
            id="special_folder_mobile",
        ),
    )

    @pytest.mark.parametrize("date_modified,special_folder,changes", test_folder_as_json)
    def test_folder_as_json(self, date_modified: int, special_folder: SpecialFolder, changes: dict):
        input_folder = Folder(
            guid="r4nJVsw0GmHo",
            title="test-title",
            index=0,
            date_added=1659184459926000,
            date_modified=date_modified,
            id=1,
            special_folder=special_folder,
            children=[],
        )

        expected_result = {
            "children": [],
            "dateAdded": 1659184459926000,
            "guid": "r4nJVsw0GmHo",
            "id": 1,
            "index": 0,
            "lastModified": 1719774198044000,
            "title": "test-title",
            "type": MOZILLA_CONTAINER_CONST,
            "typeCode": 2,
        }
        expected_result.update(changes)

        result = self.firefox._folder_as_json(input_folder)
        assert result == expected_result

    test_url_as_json_params = (
        pytest.param(
            "test-title",
            1719774198044000,
            "https://www.example.com/apple-touch-icon.png",
            {
                "lastModified": 1719774198044000,
                "iconuri": "https://www.example.com/apple-touch-icon.png",
            },
            id="url_full",
        ),
        pytest.param("test-title", 0, "", {}, id="url_minimal"),
        pytest.param(
            "test-title",
            1719774198044000,
            "",
            {"lastModified": 1719774198044000},
            id="uri_no_icon_uri",
        ),
        pytest.param("test-title", 0, "", {}, id="uri_no_date_modified"),
    )

    @pytest.mark.parametrize("title,date_modified,icon_uri,changes", test_url_as_json_params)
    def test_url_as_json(self, title: str, date_modified: int, icon_uri: str, changes: dict):
        input_url = Url(
            guid="sMWZuuDaDbKP",
            title=title,
            index=2,
            date_added=1719774198044000,
            date_modified=date_modified,
            id=45,
            url="https://www.example.com/",
            icon_uri=icon_uri,
            icon="dummy-icon",
        )

        expected_result = {
            "dateAdded": 1719774198044000,
            "guid": "sMWZuuDaDbKP",
            "id": 45,
            "index": 2,
            "lastModified": 0,
            "title": "test-title",
            "type": MOZILLA_PLACE_CONST,
            "typeCode": 1,
            "uri": "https://www.example.com/",
        }

        expected_result.update(changes)

        result = self.firefox._url_as_json(input_url)
        assert result == expected_result

    def test_ensure_mozilla_guid(self):
        guid = "0pdiR3ZFnRvz"
        result = self.firefox._ensure_mozilla_guid(guid)
        assert result == guid

    test_ensure_mozilla_guid_invalid_params = (
        pytest.param("", id="no-guid"),
        pytest.param("c4d6c7cd-5228-4d45-9317-7913b134ba38", id="uuid-type-guid"),
    )

    @pytest.mark.parametrize("guid", test_ensure_mozilla_guid_invalid_params)
    def test_ensure_mozilla_guid_invalid(self, guid: str):
        result = self.firefox._ensure_mozilla_guid(guid)
        assert len(result) == MOZILLA_GUID_LENGTH

    @pytest.mark.parametrize(
        "file_path", (TEST_FILE_FIREFOX_JSON, TEST_FILE_FIREFOX_JSON_WITH_SEPARATOR)
    )
    def test_from_json(self, file_path: Path):
        result = self.firefox.from_json(file_path)

        expected = bookmarks_json()

        assert result == expected

    test_json_to_object_folder_params = (
        pytest.param(None, {"root": ""}, id="normal_folder"),
        pytest.param(SpecialFolder.ROOT, {"root": "placesRoot"}, id="root_folder"),
        pytest.param(SpecialFolder.MENU, {"root": "bookmarksMenuFolder"}, id="menu_folder"),
        pytest.param(SpecialFolder.TOOLBAR, {"root": "toolbarFolder"}, id="toolbar_folder"),
        pytest.param(SpecialFolder.OTHER, {"root": "unfiledBookmarksFolder"}, id="other_folder"),
        pytest.param(SpecialFolder.MOBILE, {"root": "mobileFolder"}, id="mobile_folder"),
    )

    @pytest.mark.parametrize("special_folder,changes", test_json_to_object_folder_params)
    def test_json_to_object_folder(self, special_folder: SpecialFolder, changes: dict):
        folder_ = {
            "guid": "K3LUb7o0kSUt",
            "title": "Main Folder",
            "index": 0,
            "dateAdded": 1599750431776000,
            "lastModified": 1599750431776000,
            "id": 1,
            "typeCode": 2,
            "type": MOZILLA_CONTAINER_CONST,
            "children": [],
        }
        folder_.update(changes)

        id_ = int(folder_["id"])
        name = folder_["title"]
        folder = Firefox._json_as_folder(folder_)
        assert isinstance(folder, Folder)
        assert isinstance(folder.children, list)
        assert isinstance(folder.date_added, int)
        assert isinstance(folder.date_modified, int)
        assert folder.id == id_
        assert folder.title == name
        assert folder.special_folder == special_folder

    def test_json_to_object_url(self):
        url_ = {
            "guid": "7TpRGhofxKDv",
            "title": "Google",
            "index": 0,
            "dateAdded": 1599750431776000,
            "lastModified": 1599750431776000,
            "id": 2,
            "typeCode": 1,
            "iconuri": "https://www.google.com/favicon.ico",
            "type": MOZILLA_PLACE_CONST,
            "uri": "https://www.google.com",
        }

        id_ = int(url_["id"])
        title = url_["title"]
        url_address = url_["uri"]
        url = Firefox._json_as_url(url_)
        assert isinstance(url, Url)
        assert isinstance(url.date_added, int)
        assert isinstance(url.date_modified, int)
        assert url.id == id_
        assert url.title == title
        assert url.url == url_address
