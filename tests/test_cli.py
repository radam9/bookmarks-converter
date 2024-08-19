import filecmp
import sys
from argparse import ArgumentTypeError
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from conftest import (
    TEST_FILE_BOOKMARKIE_HTML,
    TEST_FILE_BOOKMARKIE_JSON,
    TEST_FILE_FIREFOX_HTML,
    TEST_INPUT_FILE,
    TEST_OUTPUT_FILE,
)

from bookmarks_converter import Bookmarkie, Chrome, Firefox
from bookmarks_converter.cli import (
    _get_version,
    _input_file,
    _output_file,
    _parse_args,
    _parse_bookmark_format,
    main,
)
from bookmarks_converter.converters.converter import Converter
from bookmarks_converter.formats import BaseFormat, DBFormat, HTMLFormat, JSONFormat

# In Python 3.10:
# Misleading phrase “optional arguments” was replaced with “options” in argparse help.
# Some tests might require adaptation if they rely on exact output match.
# https://docs.python.org/3/whatsnew/3.10.html#argparse
if sys.version_info.minor >= 10:
    optional_arguments = "options"
else:
    optional_arguments = "optional arguments"


def test_input_file():
    file_ = _input_file(str(TEST_INPUT_FILE))
    assert file_ == TEST_INPUT_FILE


def test_input_file_error():
    filepath = "imposter"
    with pytest.raises(ArgumentTypeError) as err_info:
        _input_file(filepath)
    (msg,) = err_info.value.args
    assert msg == "file not found: 'imposter'"


def test_output_file():
    file_ = _output_file(str(TEST_INPUT_FILE))
    assert file_ == TEST_INPUT_FILE


def test_output_file_error():
    filepath = TEST_OUTPUT_FILE.parent
    with pytest.raises(ArgumentTypeError) as err_info:
        _output_file(filepath)
    (msg,) = err_info.value.args
    assert msg.startswith("invalid output file: ")


USAGE_MSG = (
    "usage: bookmarks-converter [-h] [-V] -i INPUT -I INPUT_FORMAT [-o OUTPUT] -O OUTPUT_FORMAT\n"
)

test_parse_args_positional_arguments_params = (
    pytest.param(
        str(TEST_INPUT_FILE), "bookmarkie/db", "", "chrome/html", id="without-output-file"
    ),
    pytest.param(
        str(TEST_INPUT_FILE),
        "firefox/json",
        str(TEST_OUTPUT_FILE),
        "bookmarkie/json",
        id="with-output-file",
    ),
)


@pytest.mark.parametrize(
    "input_file, input_format, output_file, output_format",
    test_parse_args_positional_arguments_params,
)
def test_parse_args_positional_arguments(
    input_file: str, input_format: str, output_file: str, output_format: str
):
    input_ = Path(input_file)
    argv = ["-i", input_file, "-I", input_format, "-O", output_format]
    if output_file:
        argv.extend(["-o", output_file])
    _, args = _parse_args(argv)
    assert args.input == input_
    assert args.input_format == input_format
    assert args.output_format == output_format
    if output_file:
        assert args.output == Path(output_file)


help_error_message = (
    USAGE_MSG
    + f"\nConvert your browser bookmarks file.\n\nThe bookmark format is composed of two parts separated by a slash: [CONVERTER]/[FORMAT], ex. 'firefox/html'\nWith the converter being one of the available converters: ('bookmarkie', 'chrome', 'firefox')\nAnd the format being one of the available formats: ('db', 'html', 'json')\n\nExample Usage:\n    bookmarks-converter -i ./input_bookmarks.db --input-format 'bookmarkie/db' --output-format 'chrome/html'\n    bookmarks-converter -i ./some_bookmarks.html -I 'chrome/html' -o ./output_bookmarks.json -O 'firefox/json'\n    \n\n{optional_arguments}:\n  -h, --help            show this help message and exit\n  -V, --version         show program's version number and exit\n  -i INPUT, --input INPUT\n                        Input bookmarks file\n  -I INPUT_FORMAT, --input-format INPUT_FORMAT\n                        The bookmark format of the input bookmarks file\n  -o OUTPUT, --output OUTPUT\n                        Output bookmarks file\n  -O OUTPUT_FORMAT, --output-format OUTPUT_FORMAT\n                        The bookmark format of the output bookmarks file\n"
)

test_parse_args_with_exit_code_params = (
    pytest.param(
        [],
        2,
        "",
        USAGE_MSG
        + "bookmarks-converter: error: the following arguments are required: -i/--input, -I/--input-format, -O/--output-format\n",
        id="no_arguments",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE)],
        2,
        "",
        USAGE_MSG
        + "bookmarks-converter: error: the following arguments are required: -I/--input-format, -O/--output-format\n",
        id="only_input_filepath",
    ),
    pytest.param(
        ["-I", "firefox/json"],
        2,
        "",
        USAGE_MSG
        + "bookmarks-converter: error: the following arguments are required: -i/--input, -O/--output-format\n",
        id="only_input_format",
    ),
    pytest.param(
        ["-O", "firefox/json"],
        2,
        "",
        USAGE_MSG
        + "bookmarks-converter: error: the following arguments are required: -i/--input, -I/--input-format\n",
        id="only_output_format",
    ),
    pytest.param(
        ["-i", "non-existent-file", "-I", "firefox/json", "-O", "chrome/html"],
        2,
        "",
        USAGE_MSG
        + "bookmarks-converter: error: argument -i/--input: file not found: 'non-existent-file'\n",
        id="filepath_notfound",
    ),
    pytest.param(["-V"], 0, f"bookmarks-converter {_get_version()}\n", "", id="version"),
    pytest.param(["-h"], 0, help_error_message, "", id="help"),
    pytest.param(
        ["--version"], 0, f"bookmarks-converter {_get_version()}\n", "", id="version_long"
    ),
    pytest.param(["--help"], 0, help_error_message, "", id="help_long"),
)


@pytest.mark.parametrize("arg, exit_code, out_msg, err_msg", test_parse_args_with_exit_code_params)
def test_parse_args_with_exit_code(
    capsys, arg: list[str], exit_code: int, out_msg: str, err_msg: str
):
    with pytest.raises(SystemExit) as exc_info:
        _parse_args(arg)
    (retv,) = exc_info.value.args
    out, err = capsys.readouterr()
    assert retv == exit_code
    assert out == out_msg
    assert err == err_msg


test_parse_bookmark_format_params = (
    pytest.param("bookmarkie/db", Bookmarkie, DBFormat, id="bookmarkie/db"),
    pytest.param("bookmarkie/json", Bookmarkie, JSONFormat, id="bookmarkie/json"),
    pytest.param("chrome/html", Chrome, HTMLFormat, id="chrome/html"),
    pytest.param("chrome/json", Chrome, JSONFormat, id="chrome/json"),
    pytest.param("firefox/html", Firefox, HTMLFormat, id="firefox/html"),
    pytest.param("firefox/json", Firefox, JSONFormat, id="firefox/json"),
)


@pytest.mark.parametrize("bookmark_type,converter,format_", test_parse_bookmark_format_params)
def test_parse_bookmark_format(bookmark_type: str, converter: [Converter], format_: [BaseFormat]):
    result_converter, result_format = _parse_bookmark_format(bookmark_type)
    assert isinstance(result_converter, converter)
    assert isinstance(result_format, format_)


test_parse_bookmark_format_error_params = (
    pytest.param("a", "Invalid bookmark format: a", id="invalid-bookmark-format"),
    pytest.param(
        "chroomie/html", "Unsupported bookmark converter: chroomie", id="invalid-bookmark-converter"
    ),
    pytest.param(
        "chrome/db",
        "The converter 'Chrome' doesn't support the format 'db'",
        id="Unsupported-bookmark-format",
    ),
)


@pytest.mark.parametrize("bookmark_type,err_msg", test_parse_bookmark_format_error_params)
def test_parse_bookmark_format_error(bookmark_type: str, err_msg: str):
    with pytest.raises(ValueError) as err_info:
        _, _ = _parse_bookmark_format(bookmark_type)

    assert err_info.value.args[0] == err_msg


test_main_params = (
    pytest.param(
        TEST_FILE_BOOKMARKIE_JSON,
        "bookmarkie/json",
        "bookmarkie/html",
        TEST_FILE_BOOKMARKIE_HTML,
        id="bookmarkie-json_to_bookmarkie-html",
    ),
    pytest.param(
        TEST_FILE_BOOKMARKIE_JSON,
        "bookmarkie/json",
        "bookmarkie/json",
        TEST_FILE_BOOKMARKIE_JSON,
        id="bookmarkie-json_to_bookmarkie-json",
    ),
    pytest.param(
        TEST_FILE_BOOKMARKIE_JSON,
        "bookmarkie/json",
        "firefox/html",
        TEST_FILE_FIREFOX_HTML,
        id="bookmarkie-json_to_firefox-html",
    ),
)


@pytest.mark.parametrize("input_file,input_format,output_format,expected_result", test_main_params)
def test_main(
    capsys, input_file: Path, input_format: str, output_format: str, expected_result: Path
):
    with TemporaryDirectory() as tmpdir:
        output_filepath = Path(tmpdir).joinpath("output_file")
        output_filepath.touch(0o664, exist_ok=True)
        exit_code = main(
            [
                "-i",
                str(input_file),
                "-I",
                input_format,
                "-O",
                output_format,
                "-o",
                str(output_filepath),
            ]
        )
        out, err = capsys.readouterr()
        assert exit_code == 0
        assert (
            out
            == f"Conversion successful!\nThe converted file can be found at '{output_filepath}'\n"
        )
        assert err == ""

        assert filecmp.cmp(output_filepath, expected_result)


test_main_error_params = (
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "bookmarkie/db", "-O", "firefox/json"],
        USAGE_MSG
        + f"bookmarks-converter: error: The provided file '{str(TEST_INPUT_FILE)}' is not a valid sqlite3 database file.\n",
        id="not_database",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "bookmarkie/json", "-O", "firefox/json"],
        USAGE_MSG
        + f"bookmarks-converter: error: The provided file '{str(TEST_INPUT_FILE)}' is not a valid bookmarks file.\n",
        id="not_json",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "firefox/html", "-O", "firefox/json"],
        USAGE_MSG
        + f"bookmarks-converter: error: The provided file '{str(TEST_INPUT_FILE)}' is not a valid bookmarks file.\n",
        id="not_html",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "a", "-O", "firefox/json"],
        USAGE_MSG + "bookmarks-converter: error: Invalid bookmark format: a\n",
        id="invalid_input_format",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "firefox/json", "-O", "a"],
        USAGE_MSG + "bookmarks-converter: error: Invalid bookmark format: a\n",
        id="invalid_output_format",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "firefox/x", "-O", "firefox/json"],
        USAGE_MSG + "bookmarks-converter: error: 'x' is not a valid Format\n",
        id="invalid_input_format_type",
    ),
    pytest.param(
        ["-i", str(TEST_INPUT_FILE), "-I", "firefox/json", "-O", "firefox/x"],
        USAGE_MSG + "bookmarks-converter: error: 'x' is not a valid Format\n",
        id="invalid_output_format_type",
    ),
)


@pytest.mark.parametrize("args, err_msg", test_main_error_params)
def test_main_error(capsys, args: list[str], err_msg: str):
    with pytest.raises(SystemExit) as err_info:
        main(args)
    (retv,) = err_info.value.args
    out, err = capsys.readouterr()
    assert retv == 2
    assert out == ""
    assert err == err_msg
