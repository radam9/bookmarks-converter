from pathlib import Path

from conftest import (
    TEST_FILE_BOOKMARKIE_HTML,
    TEST_FILE_BOOKMARKIE_HTML_FORMATTED,
    TEST_FILE_BOOKMARKIE_HTML_UNINDENTED,
)

from bookmarks_converter.util import format_html, indent_html


def test_format_html():
    result = format_html(Path(TEST_FILE_BOOKMARKIE_HTML))

    with TEST_FILE_BOOKMARKIE_HTML_FORMATTED.open("r", encoding="utf-8") as f:
        expected = f.read()

    assert result == expected


def test_indent_html():
    with TEST_FILE_BOOKMARKIE_HTML_UNINDENTED.open("r", encoding="utf-8") as f:
        content = f.read()

    result = indent_html(content)

    with TEST_FILE_BOOKMARKIE_HTML.open("r", encoding="utf-8") as f:
        expected = f.read()

    assert result == expected
