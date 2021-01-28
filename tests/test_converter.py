from filecmp import cmp
from pathlib import Path

import pytest
from bookmarks_converter import BookmarksConverter


@pytest.mark.parametrize(
    "result_file, source_file",
    [
        ("from_chrome_json.html", "from_chrome_json.db"),
        ("from_firefox_json.html", "from_firefox_json.db"),
    ],
)
def test_from_db_to_html(result_file, source_file, result_bookmark_files):
    result_file = Path(result_bookmark_files[result_file])
    source_file = Path(result_bookmark_files[source_file])
    bookmarks = BookmarksConverter(source_file)
    bookmarks.parse("db")
    bookmarks.convert("html")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".html")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_db_to_json_chrome(result_bookmark_files):
    result_file = Path(result_bookmark_files["from_chrome_html.json"])
    source_file = Path(result_bookmark_files["from_chrome_html.db"])
    bookmarks = BookmarksConverter(source_file)
    bookmarks.parse("db")
    # change the root and other folder dates, as they are generated when they
    # are created and don't exist in an html file.
    bookmarks._tree.date_added = 1601886282042
    bookmarks._tree.children[1].date_added = 1601886282042
    bookmarks.convert("json")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".json")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_db_to_json_firefox(result_bookmark_files):
    result_file = Path(result_bookmark_files["from_firefox_html.json"])
    source_file = Path(result_bookmark_files["from_firefox_html.db"])
    bookmarks = BookmarksConverter(source_file)
    bookmarks.parse("db")
    # change the root, menu and toolber folder dates, as they are generated
    # when they are created and don't exist in an html file.
    bookmarks._tree.date_added = 1601886171439
    bookmarks._tree.children[0].date_added = 1601886171439
    bookmarks.convert("json")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".json")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_chrome_html_to_json(
    source_bookmark_files, result_bookmark_files, read_json
):
    result_file = Path(result_bookmark_files["from_chrome_html.json"])
    json_data = read_json(result_file)
    # date_added of "root" folder
    root_date = json_data["date_added"]
    # date_added of "Other Bookmarks" folder
    other_date = json_data["children"][1]["date_added"]
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.html"])
    bookmarks.parse("html")
    bookmarks.convert("json")
    bookmarks.bookmarks["date_added"] = root_date
    bookmarks.bookmarks["children"][1]["date_added"] = other_date
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".json")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_chrome_html_to_db(
    source_bookmark_files, result_bookmark_files, get_data_from_db
):
    origin = "Chrome"
    result_file = Path(result_bookmark_files["from_chrome_html.db"])
    result_bookmarks, root_date, other_date = get_data_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.html"])
    bookmarks.parse("html")
    bookmarks.convert("db")
    bookmarks.bookmarks[0].date_added = root_date
    bookmarks.bookmarks[1].date_added = other_date
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_data_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()


def test_from_chrome_json_to_html(source_bookmark_files, result_bookmark_files):
    result_file = Path(result_bookmark_files["from_chrome_json.html"])
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.json"])
    bookmarks.parse("json")
    bookmarks.convert("html")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".html")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_chrome_json_to_db(
    source_bookmark_files, result_bookmark_files, get_data_from_db
):
    origin = "Chrome"
    result_file = Path(result_bookmark_files["from_chrome_json.db"])
    result_bookmarks, _, _ = get_data_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_chrome.json"])
    bookmarks.parse("json")
    bookmarks.convert("db")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_data_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()


def test_from_firefox_html_to_json(
    source_bookmark_files, result_bookmark_files, read_json
):
    result_file = Path(result_bookmark_files["from_firefox_html.json"])
    json_data = read_json(result_file)
    # date_added of "root" folder
    root_date = json_data["date_added"]
    # date_added of "Bookmarks Menu" folder
    menu_date = json_data["children"][0]["date_added"]
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.html"])
    bookmarks.parse("html")
    bookmarks.convert("json")
    bookmarks.bookmarks["date_added"] = root_date
    bookmarks.bookmarks["children"][0]["date_added"] = menu_date
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".json")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_firefox_html_to_db(
    source_bookmark_files, result_bookmark_files, get_data_from_db
):
    origin = "Firefox"
    result_file = Path(result_bookmark_files["from_firefox_html.db"])
    result_bookmarks, root_date, menu_date = get_data_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.html"])
    bookmarks.parse("html")
    bookmarks.convert("db")
    bookmarks.bookmarks[0].date_added = root_date
    bookmarks.bookmarks[13].date_added = menu_date
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_data_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()


def test_from_firefox_json_to_html(source_bookmark_files, result_bookmark_files):
    result_file = Path(result_bookmark_files["from_firefox_json.html"])
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.json"])
    bookmarks.parse("json")
    bookmarks.convert("html")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".html")
    assert cmp(result_file, output_file, shallow=False)
    output_file.unlink()


def test_from_firefox_json_to_db(
    source_bookmark_files, result_bookmark_files, get_data_from_db
):
    origin = "Firefox"
    result_file = Path(result_bookmark_files["from_firefox_json.db"])
    result_bookmarks, _, _ = get_data_from_db(result_file, origin)
    bookmarks = BookmarksConverter(source_bookmark_files["bookmarks_firefox.json"])
    bookmarks.parse("json")
    bookmarks.convert("db")
    bookmarks.save()
    output_file = bookmarks.output_filepath.with_suffix(".db")
    output_bookmarks, _, _ = get_data_from_db(output_file, origin)
    assert result_bookmarks == output_bookmarks
    output_file.unlink()
