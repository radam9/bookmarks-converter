import itertools
from argparse import ArgumentTypeError
from pathlib import Path

import pytest
from bookmarks_converter.cli import _file, _get_version, _parse_args, main


def test_file_error():
    filepath = "imposter"
    with pytest.raises(ArgumentTypeError) as errinfo:
        _file(filepath)
    (msg,) = errinfo.value.args
    assert msg == "Could not find a file at the given filepath: 'imposter'"


def test_file():
    filepath = "LICENSE"
    file_ = _file(filepath)
    assert file_ == Path(filepath)


usage = "usage: bookmarks-converter [-h] [-V] input_format output_format filepath\n"

errors = {
    "no_arguments": usage
    + "bookmarks-converter: error: the following arguments are required: input_format, output_format, filepath\n",
    "incorrect_input_format": usage
    + "bookmarks-converter: error: argument input_format: invalid choice: 'a' (choose from 'db', 'html', 'json')\n",
    "2_missing_arguments": usage
    + "bookmarks-converter: error: the following arguments are required: output_format, filepath\n",
    "incorrect_output_format": usage
    + "bookmarks-converter: error: argument output_format: invalid choice: 'a' (choose from 'db', 'html', 'json')\n",
    "filepath_missing": usage
    + "bookmarks-converter: error: the following arguments are required: filepath\n",
    "filepath_notfound": usage
    + "bookmarks-converter: error: argument filepath: Could not find a file at the given filepath: 'a'\n",
    "version": f"bookmarks-converter {_get_version()}\n",
    "help": usage
    + "\nConvert your browser bookmarks file from (db, html, json) to (db, html, json).\n\npositional arguments:\n  input_format   Format of the input bookmarks file. one of (db, html, json).\n  output_format  Format of the output bookmarks file. one of (db, html, json).\n  filepath       Path to bookmarks file to convert.\n\noptional arguments:\n  -h, --help     show this help message and exit\n  -V, --version  show program's version number and exit\n",
}

choices = ["db", "html", "json"]


@pytest.mark.parametrize(
    "input_format, output_format, filepath",
    list(itertools.product(choices, choices, ("LICENSE",))),
)
def test_parse_args_positional_arguments(input_format, output_format, filepath):
    _, args = _parse_args([input_format, output_format, filepath])
    assert args.input_format == input_format
    assert args.output_format == output_format
    assert args.filepath == Path(filepath)


titles = [*errors.keys(), "version_long", "help_long"]
checks = [
    ([], 2, "", errors.get("no_arguments")),
    (["a"], 2, "", errors.get("incorrect_input_format")),
    (["db"], 2, "", errors.get("2_missing_arguments")),
    (["db", "a"], 2, "", errors.get("incorrect_output_format")),
    (["db", "json"], 2, "", errors.get("filepath_missing")),
    (["db", "json", "a"], 2, "", errors.get("filepath_notfound")),
    (["-V"], 0, errors.get("version"), ""),
    (["-h"], 0, errors.get("help"), ""),
    (["--version"], 0, errors.get("version"), ""),
    (["--help"], 0, errors.get("help"), ""),
]


@pytest.mark.parametrize("arg, exit_code, out_msg, err_msg", checks, ids=titles)
def test_parse_args_with_exit_code(capsys, arg, exit_code, out_msg, err_msg):
    with pytest.raises(SystemExit) as excinfo:
        _parse_args(arg)
    (retv,) = excinfo.value.args
    out, err = capsys.readouterr()
    assert retv == exit_code
    assert out == out_msg
    assert err == err_msg


run_errors = {
    "not_database": usage
    + "bookmarks-converter: error: The provided file 'LICENSE' is not a valid sqlite3 database file.\n",
    "not_json": usage
    + "bookmarks-converter: error: The provided file 'LICENSE' is not a valid bookmarks file.\n",
    "not_html": usage
    + "bookmarks-converter: error: The provided file 'LICENSE' is not a valid bookmarks file.\n",
}


@pytest.mark.parametrize(
    "args, err_msg",
    [
        (["db", "db", "LICENSE"], run_errors.get("not_database")),
        (["json", "json", "LICENSE"], run_errors.get("not_json")),
        (["html", "html", "LICENSE"], run_errors.get("not_html")),
    ],
    ids=run_errors.keys(),
)
def test_main_error(capsys, args, err_msg):
    with pytest.raises(SystemExit) as errinfo:
        main(args)
    (retv,) = errinfo.value.args
    out, err = capsys.readouterr()
    assert retv == 2
    assert out == ""
    assert err == err_msg


def test_main(capsys, result_bookmark_files):
    filepath = Path(result_bookmark_files["from_chrome_html.db"])
    output_filepath = filepath.with_name(f"output_{filepath.stem}_001{filepath.suffix}")
    exit_code = main(["db", "db", str(filepath)])
    out, err = capsys.readouterr()
    assert exit_code == 0
    assert (
        out
        == f"Conversion successful!\nThe converted file can be found at '{output_filepath}'\n"
    )
    assert err == ""
    output_filepath.unlink()
