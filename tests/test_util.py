from pathlib import Path

from conftest import (
    TEST_FILE_FIREFOX_HTML,
    TEST_FILE_FIREFOX_HTML_FORMATTED,
    TEST_FILE_FIREFOX_HTML_UNINDENTED,
)

from bookmarks_converter.util import format_html, indent_html


def test_format_html():
    result = format_html(Path(TEST_FILE_FIREFOX_HTML))

    with open(TEST_FILE_FIREFOX_HTML_FORMATTED, "r") as f:
        expected = f.read()

    assert result == expected


def test_indent_html():
    with open(TEST_FILE_FIREFOX_HTML_UNINDENTED, "r") as f:
        content = f.read()

    result = indent_html(content)

    with open(TEST_FILE_FIREFOX_HTML, "r") as f:
        expected = f.read()

    assert result == expected
