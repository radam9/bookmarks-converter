from uuid import UUID, uuid4

import pytest
from conftest import TEST_FILE_BOOKMARKIE_DB, TEST_FILE_BOOKMARKIE_HTML, TEST_FILE_BOOKMARKIE_JSON
from resources.bookmarks_bookmarkie import bookmarks_html, bookmarks_json

from bookmarks_converter.converters.bookmarkie import (
    BOOKMARKIE_BOOKMARKS_MENU_FOLDER_TITLE,
    BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE,
    BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE,
    BOOKMARKIE_BOOKMARKS_ROOT_FOLDER_TITLE,
    BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE,
    Bookmarkie,
    FolderRoot,
)
from bookmarks_converter.models import DBFolder, DBUrl, Folder, HTMLBookmark, SpecialFolder, Url


class TestBookmarkie:
    bookmarkie = Bookmarkie()

    def test_as_db(self, get_data_from_db):
        result = self.bookmarkie.as_db(bookmarks_json())

        expected = get_data_from_db(TEST_FILE_BOOKMARKIE_DB)

        assert result == expected

    test_folder_as_dbfolder_params = (
        pytest.param(None, id="normal_folder"),
        pytest.param(SpecialFolder.ROOT, id="root_folder"),
        pytest.param(SpecialFolder.MENU, id="menu_folder"),
        pytest.param(SpecialFolder.TOOLBAR, id="toolbar_folder"),
        pytest.param(SpecialFolder.OTHER, id="other_folder"),
        pytest.param(SpecialFolder.MOBILE, id="mobile_folder"),
    )

    @pytest.mark.parametrize("special_folder", test_folder_as_dbfolder_params)
    def test_folder_as_dbfolder(self, special_folder: SpecialFolder):
        input_folder = Folder(
            guid="e2ef11d8-276f-4cfb-92ff-5c94deabb16b",
            title="test-title",
            index=0,
            date_added=1659184459926000,
            date_modified=1678636323216000,
            id=2,
            special_folder=special_folder,
            children=[],
        )

        expected_result = DBFolder(
            _id=input_folder.id,
            guid=input_folder.guid,
            index=input_folder.index,
            parent_id=9000,
            title=input_folder.title,
            date_added=input_folder.date_added,
            date_modified=input_folder.date_modified,
        )
        folder_root = None
        if special_folder:
            folder_root = FolderRoot(special_folder).name

        expected_result.special_folder = folder_root

        result = self.bookmarkie._folder_as_dbfolder(input_folder, 9000)
        assert result == expected_result

    def test_url_as_dburl(self):
        input_url = Url(
            guid="D7oNqJF2nvDL",
            title="test-title",
            index=7,
            date_added=1599750511000000,
            date_modified=1719772224487000,
            id=8,
            url="https://www.example.com/",
        )

        expected_result = DBUrl(
            _id=input_url.id,
            guid=input_url.guid,
            index=input_url.index,
            parent_id=9000,
            title=input_url.title,
            date_added=input_url.date_added,
            date_modified=input_url.date_modified,
            url=input_url.url,
            icon=input_url.icon,
            icon_uri=input_url.icon_uri,
            tags=",".join(input_url.tags),
        )

        result = self.bookmarkie._url_as_dburl(input_url, 9000)
        assert result == expected_result

    def test_from_db(self):
        result = self.bookmarkie.from_db(TEST_FILE_BOOKMARKIE_DB)

        expected = bookmarks_json()

        assert result == expected

    def test_as_html(self):
        result = self.bookmarkie.as_html(bookmarks_html())

        with open(TEST_FILE_BOOKMARKIE_HTML, "r") as f:
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
        pytest.param(
            "some title",
            1719774198044000,
            SpecialFolder.MOBILE,
            '<DT><H3 ADD_DATE="1659184459" LAST_MODIFIED="1719774198" MOBILE_BOOKMARKS_FOLDER="true">Mobile Bookmarks</H3>\n',
            id="special_folder_mobile",
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
        result = self.bookmarkie._folder_as_html(input_folder)
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

        result = self.bookmarkie._url_as_html(input_url)
        assert result == expected_result

    def test_from_html(self, modify_folder_and_url_methods):
        result = self.bookmarkie.from_html(TEST_FILE_BOOKMARKIE_HTML)

        expected = bookmarks_html()

        # the root and menu folder have the time generated during parsing, so we make them equal.
        expected.date_added = result.date_added
        expected.children[0].date_added = result.children[0].date_added

        assert result == expected

    test_get_html_special_folder_params = (
        pytest.param("test-title", None, id="normal_folder"),
        pytest.param(BOOKMARKIE_BOOKMARKS_MENU_FOLDER_TITLE, SpecialFolder.MENU, id="menu_folder"),
        pytest.param(
            BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE, SpecialFolder.TOOLBAR, id="toolbar_folder"
        ),
        pytest.param(
            BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE, SpecialFolder.OTHER, id="other_folder"
        ),
        pytest.param(
            BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE, SpecialFolder.MOBILE, id="mobile_folder"
        ),
    )

    @pytest.mark.parametrize("title,special_folder", test_get_html_special_folder_params)
    def test_get_html_special_folder(self, title: str, special_folder: SpecialFolder):
        input_folder = HTMLBookmark(attrs={"title": title}, name="folder")
        result = self.bookmarkie._get_html_special_folder(input_folder)
        assert result == special_folder

    def test_as_json(self, read_json):
        result = self.bookmarkie.as_json(bookmarks_json())

        expected = read_json(TEST_FILE_BOOKMARKIE_JSON)

        assert result == expected

    test_folder_as_json = (
        pytest.param(None, {}, id="normal_folder"),
        pytest.param(
            SpecialFolder.ROOT,
            {"special_folder": "root", "title": BOOKMARKIE_BOOKMARKS_ROOT_FOLDER_TITLE},
            id="special_folder_root",
        ),
        pytest.param(
            SpecialFolder.TOOLBAR,
            {"special_folder": "toolbar", "title": BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE},
            id="special_folder_toolbar",
        ),
        pytest.param(
            SpecialFolder.OTHER,
            {"special_folder": "other", "title": BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE},
            id="special_folder_other",
        ),
        pytest.param(
            SpecialFolder.MOBILE,
            {"special_folder": "mobile", "title": BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE},
            id="special_folder_mobile",
        ),
    )

    @pytest.mark.parametrize("special_folder,changes", test_folder_as_json)
    def test_folder_as_json(self, special_folder: SpecialFolder, changes: dict):
        input_folder = Folder(
            guid="c4d6c7cd-5228-4d45-9317-7913b134ba38",
            title="test-title",
            index=0,
            date_added=1659184459926000,
            date_modified=1719774198044000,
            id=1,
            special_folder=special_folder,
            children=[],
        )

        expected_result = {
            "children": [],
            "date_added": 1659184459926000,
            "guid": "c4d6c7cd-5228-4d45-9317-7913b134ba38",
            "id": 1,
            "index": 0,
            "date_modified": 1719774198044000,
            "title": "test-title",
            "type": "folder",
        }
        expected_result.update(changes)

        result = self.bookmarkie._folder_as_json(input_folder)
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
            "date_added": 1719774198044000,
            "guid": "a8b6cce8-7bee-4840-ad9a-7c4684054e57",
            "id": 45,
            "index": 2,
            "date_modified": 1719774198044000,
            "title": "test-title",
            "type": "url",
            "url": "https://www.example.com/",
            "icon": "dummy-icon",
            "iconuri": "https://www.example.com/apple-touch-icon.png",
            "tags": [],
        }

        result = self.bookmarkie._url_as_json(input_url)
        assert result == expected_result

    def test_ensure_guid(self):
        guid = "a8b6cce8-7bee-4840-ad9a-7c4684054e57"
        result = self.bookmarkie._ensure_guid(guid)
        assert UUID(result)
        assert result == guid

    def test_ensure_guid_non_uuid(self):
        guid = "some-random-non-uuid-guid"
        result = self.bookmarkie._ensure_guid(guid)
        assert UUID(result)
        assert result != guid

    def test_from_json(self):
        result = self.bookmarkie.from_json(TEST_FILE_BOOKMARKIE_JSON)

        expected = bookmarks_json()

        assert result == expected

    test_json_to_object_folder_params = (
        pytest.param(None, {}, id="normal_folder"),
        pytest.param(
            SpecialFolder.ROOT,
            {"special_folder": "root", "title": BOOKMARKIE_BOOKMARKS_ROOT_FOLDER_TITLE},
            id="root_folder",
        ),
        pytest.param(
            SpecialFolder.MENU,
            {"special_folder": "menu", "title": BOOKMARKIE_BOOKMARKS_MENU_FOLDER_TITLE},
            id="menu_folder",
        ),
        pytest.param(
            SpecialFolder.TOOLBAR,
            {"special_folder": "toolbar", "title": BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE},
            id="toolbar_folder",
        ),
        pytest.param(
            SpecialFolder.OTHER,
            {"special_folder": "other", "title": BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE},
            id="other_folder",
        ),
        pytest.param(
            SpecialFolder.MOBILE,
            {"special_folder": "mobile", "title": BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE},
            id="mobile_folder",
        ),
    )

    @pytest.mark.parametrize("special_folder,changes", test_json_to_object_folder_params)
    def test_json_to_object_folder(self, special_folder: SpecialFolder, changes: dict):
        _folder = {
            "type": "folder",
            "id": 1,
            "index": 0,
            "title": "Main Folder",
            "date_added": 0,
            "children": [],
        }
        _folder.update(changes)

        id_ = int(_folder["id"])
        title = _folder["title"]
        folder = Bookmarkie._json_to_object(_folder)
        assert isinstance(folder, Folder)
        assert isinstance(folder.children, list)
        assert isinstance(folder.date_added, int)
        assert isinstance(folder.date_modified, int)
        assert folder.id == id_
        assert folder.title == title
        assert folder.special_folder == special_folder

    def test_json_to_object_url(self):
        url_ = {
            "type": "url",
            "id": 2,
            "index": 0,
            "url": "https://www.example.com",
            "title": "test-title",
            "date_added": 0,
            "icon": None,
            "iconuri": "https://www.example.com/favicon.ico",
            "tags": None,
        }

        id_ = int(url_["id"])
        title = url_["title"]
        url_address = url_["url"]
        url = Bookmarkie._json_to_object(url_)
        assert isinstance(url, Url)
        assert isinstance(url.date_added, int)
        assert isinstance(url.date_modified, int)
        assert url.id == id_
        assert url.title == title
        assert url.url == url_address
