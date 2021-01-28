import json
from filecmp import cmp
from pathlib import Path

import pytest
from bookmarks_converter import BookmarksConverter
from bookmarks_converter.core import JSONMixin
from bookmarks_converter.models import Folder, JSONBookmark
from pytest_mock import class_mocker as mocker


class Test_DBMixin:
    def test_parse_db(self, result_bookmark_files, get_data_from_db):
        file_path = result_bookmark_files["from_chrome_html.db"]
        instance = BookmarksConverter(file_path)
        instance.parse("db")
        bookmarks, _, _ = get_data_from_db(file_path, "Chrome")
        assert bookmarks[0] == instance._tree

    def test_convert_to_db(self, mocker):
        mocky = mocker.patch.object(BookmarksConverter, "_iterate_folder_db")
        instance = BookmarksConverter("filepath")
        instance._tree = "test"
        instance._convert_to_db()
        assert isinstance(instance._stack, list)
        assert len(instance._stack) == 0
        assert mocky.call_count == 1

    def test_save_to_db(self, get_data_from_db):
        file_path = "temp.db"
        bookmarks = list()
        for i in range(1, 11):
            parent_id = None if i == 0 else 0
            bookmarks.append(
                Folder(date_added=0, index=0, _id=i, parent_id=parent_id, title="Title")
            )
        instance = BookmarksConverter(file_path)
        instance.bookmarks = bookmarks
        # setting the _export attribute as not to raise an error
        # setting the _format attribute for the desired output format
        instance._export = instance._format = "db"
        instance.save()
        output_file = instance.output_filepath
        temp_bookmarks, _, _ = get_data_from_db(output_file, None)
        assert bookmarks == temp_bookmarks
        output_file.unlink()


class Test_HTMLMixin:
    def test_save_to_html(self, result_bookmark_files):
        result_file = result_bookmark_files["from_firefox_json.html"]
        instance = BookmarksConverter(result_file)
        with open(result_file, "r", encoding="utf-8") as file_:
            instance.bookmarks = file_.read()
        output_file = Path(result_file).with_name("output_file.html")
        instance.output_filepath = output_file
        # setting the _export and _format attributes manually.
        instance._export = "html"
        instance._format = "html"
        instance.save()
        assert cmp(result_file, output_file, shallow=False)
        output_file.unlink()


class Test_JSONMixin:
    def test_json_to_object_folder(self, folder_custom):
        folder = JSONMixin._json_to_object(folder_custom)
        assert isinstance(folder, JSONBookmark)
        for key, value in folder_custom.items():
            assert value == getattr(folder, key)

    def test_json_to_object_url(self, url_custom):
        url = JSONMixin._json_to_object(url_custom)
        assert isinstance(url, JSONBookmark)
        for key, value in url_custom.items():
            if key == "iconuri":
                assert value == url.icon_uri
            else:
                assert value == getattr(url, key)

    def test_format_json_file_chrome(self, source_bookmark_files, read_json):
        source_file = source_bookmark_files["bookmarks_chrome.json"]
        output_file = Path(source_file).with_name("temporary.json")
        BookmarksConverter.format_json_file(source_file, output_file)
        json_data = read_json(output_file)
        assert json_data.get("name") == "root"
        assert json_data.get("children")[0].get("name") == "Bookmarks bar"
        assert json_data.get("children")[1].get("name") == "Other Bookmarks"
        output_file.unlink()

    def test_format_json_file_firefox(self, source_bookmark_files, read_json):
        source_file = source_bookmark_files["bookmarks_firefox.json"]
        output_file = Path(source_file).with_name("temporary.json")
        BookmarksConverter.format_json_file(source_file, output_file)
        json_data = read_json(output_file)
        root_children = json_data.get("children")
        assert root_children[0].get("title") == "Bookmarks Menu"
        assert root_children[1].get("title") == "Bookmarks Toolbar"
        assert root_children[2].get("title") == "Other Bookmarks"
        assert root_children[3].get("title") == "Mobile Bookmarks"
        output_file.unlink()

    def test_save_to_json(self, result_bookmark_files):
        result_file = result_bookmark_files["from_firefox_html.json"]
        instance = BookmarksConverter(result_file)
        with open(result_file, "r", encoding="utf-8") as file_:
            instance.bookmarks = json.load(file_)
        output_file = Path(result_file).with_name("output_file.json")
        instance.output_filepath = output_file
        # setting the _export and _format attributes manually.
        instance._export = "json"
        instance._format = "json"
        instance.save()
        assert cmp(result_file, output_file, shallow=False)
        output_file.unlink()


class Test_BookmarksConverter:
    def test_init(self):
        file_path = Path("/home/user/Downloads/source/bookmarks.html")
        output_file = file_path.with_name(f"output_{file_path.name}")
        temp_file = file_path.with_name(f"temp_{file_path.name}")
        instance = BookmarksConverter(str(file_path))
        assert instance.bookmarks is None
        assert instance._export is None
        assert instance._format is None
        assert instance._stack is None
        assert instance._stack_item is None
        assert instance._tree is None
        assert instance.filepath == file_path
        assert isinstance(instance.filepath, Path)
        assert instance.output_filepath == output_file
        assert instance.temp_filepath == temp_file

    def test_prepare_filepaths(self):
        filename = "/home/user/Downloads/source/bookmarks.html"
        temp_filepath = Path("/home/user/Downloads/source/temp_bookmarks.html")
        output_filepath = Path("/home/user/Downloads/source/output_bookmarks.html")
        bookmarks = BookmarksConverter(filename)
        assert temp_filepath == bookmarks.temp_filepath
        assert output_filepath == bookmarks.output_filepath

    @pytest.mark.parametrize(
        "_format, method",
        [
            ("db", "_parse_db"),
            ("json", "_parse_json"),
            ("html", "_parse_html"),
            ("DB", "_convert_to_db"),
            ("JSon", "_convert_to_json"),
            ("HTML", "_convert_to_html"),
            ("db", "_save_to_db"),
            ("json", "_save_to_json"),
            ("html", "_save_to_html"),
        ],
    )
    def test_dispatcher(self, _format, method, mocker):
        lower_format = _format.lower()
        mocky = mocker.patch.object(BookmarksConverter, method)
        instance = BookmarksConverter("filepath")
        instance._export = lower_format
        instance._format = lower_format
        instance._dispatcher(method)
        mocky.assert_called_once()

    def test_dispatcher_error(self):
        instance = BookmarksConverter("filepath")
        instance._format = "wrong format"
        with pytest.raises(TypeError) as e:
            instance._dispatcher("method")

    @pytest.mark.parametrize("_format", ["db", "json", "html"])
    def test_parse(self, _format, mocker):
        mocky = mocker.patch.object(BookmarksConverter, "_dispatcher")
        method = f"_parse_{_format}"
        instance = BookmarksConverter("filepath")
        instance.parse(_format)
        assert instance._format == _format
        mocky.assert_called_once_with(method)

    @pytest.mark.parametrize("_format", ["db", "json", "html"])
    def test_convert(self, _format, mocker):
        mocky = mocker.patch.object(BookmarksConverter, "_dispatcher")
        method = f"_convert_to_{_format}"
        instance = BookmarksConverter("filepath")
        instance.convert(_format)
        assert instance._export == _format
        assert instance._format == _format
        mocky.assert_called_once_with(method)

    @pytest.mark.parametrize("_format", ["db", "json", "html"])
    def test_save(self, _format, mocker):
        mocky = mocker.patch.object(BookmarksConverter, "_dispatcher")
        method = f"_save_to_{_format}"
        instance = BookmarksConverter("filepath")
        instance._export = _format
        instance._format = _format
        instance.save()
        mocky.assert_called_once_with(method)

    def test_save_error(self):
        instance = BookmarksConverter("filepath")
        with pytest.raises(RuntimeError) as e:
            instance.save()
