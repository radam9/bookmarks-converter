import argparse
import sys
from json import JSONDecodeError
from pathlib import Path

from sqlalchemy.exc import DatabaseError, OperationalError

from .core import BookmarksConverter


def _get_version():
    """Get bookmarks-converter version."""
    try:
        import importlib.metadata as importlib_metadata
    except ModuleNotFoundError:
        import importlib_metadata

    return importlib_metadata.version("bookmarks-converter")


def _file(filepath):
    """Check that file exists at the given path."""
    filepath = Path(filepath)

    if not filepath.is_file():
        raise argparse.ArgumentTypeError(
            f"Could not find a file at the given filepath: '{filepath}'"
        )
    return filepath


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="bookmarks-converter",
        description="Convert your browser bookmarks file from (db, html, json) to (db, html, json).",
    )

    version = _get_version()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    parser.add_argument(
        "input_format",
        choices=("db", "html", "json"),
        metavar="input_format",
        help="Format of the input bookmarks file. one of (%(choices)s).",
    )
    parser.add_argument(
        "output_format",
        choices=("db", "html", "json"),
        metavar="output_format",
        help="Format of the output bookmarks file. one of (%(choices)s).",
    )
    parser.add_argument(
        "filepath", type=_file, help="Path to bookmarks file to convert."
    )
    args = parser.parse_args(argv)
    return parser, args


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]

    parser, args = _parse_args(argv)
    filepath = args.filepath

    try:
        bookmarks = BookmarksConverter(filepath)
        bookmarks.parse(args.input_format)
        bookmarks.convert(args.output_format)
        bookmarks.save()
    except (DatabaseError, OperationalError):
        parser.error(
            f"The provided file '{filepath}' is not a valid sqlite3 database file."
        )
    except (AttributeError, JSONDecodeError, KeyError, TypeError, ValueError):
        parser.error(f"The provided file '{filepath}' is not a valid bookmarks file.")
    except Exception:
        parser.error(f"RuntimeError: An unexpected error has occured.")
    finally:
        temp_file = bookmarks.temp_filepath
        if temp_file.is_file():
            temp_file.unlink()

    sys.stdout.buffer.write(
        bytes(
            f"Conversion successful!\nThe converted file can be found at '{bookmarks.output_filepath}'\n",
            "utf-8",
        )
    )

    return 0
