import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

from sqlalchemy.exc import DatabaseError, OperationalError

from bookmarks_converter.converters import CONVERTER_FORMATS, CONVERTER_NAMES, CONVERTERS
from bookmarks_converter.converters.converter import Converter
from bookmarks_converter.formats import FORMATS, BaseFormat, Format, _new_file_name


def _get_version():
    """Get bookmarks-converter version."""
    return importlib.metadata.version("bookmarks-converter")


def _input_file(filepath: str) -> Path:
    """Check that file exists at the given path."""
    filepath = Path(filepath)

    if not filepath.is_file():
        raise argparse.ArgumentTypeError(f"file not found: '{filepath}'")
    return filepath


def _output_file(filepath: str) -> Path:
    filepath = Path(filepath)

    if filepath.is_dir():
        raise argparse.ArgumentTypeError(f"invalid output file: '{filepath}'")
    return filepath


def _parse_args(argv):
    bookmarks_type_help_text = f"""Convert your browser bookmarks file.\n\n
The bookmark format is composed of two parts separated by a slash: [CONVERTER]/[FORMAT], ex. 'firefox/html'
With the converter being one of the available converters: {CONVERTER_NAMES}
And the format being one of the available formats: {CONVERTER_FORMATS}

Example Usage:
    bookmarks-converter -i ./input_bookmarks.db --input-format 'bookmarkie/db' --output-format 'chrome/html'
    bookmarks-converter -i ./some_bookmarks.html -I 'chrome/html' -o ./output_bookmarks.json -O 'firefox/json'
    """

    formatter = lambda prog: argparse.RawTextHelpFormatter(prog, width=100)
    parser = argparse.ArgumentParser(
        prog="bookmarks-converter",
        description=bookmarks_type_help_text,
        formatter_class=formatter,
    )

    version = _get_version()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    parser.add_argument(
        "-i", "--input", type=_input_file, help="Input bookmarks file", required=True
    )
    parser.add_argument(
        "-I",
        "--input-format",
        help="The bookmark format of the input bookmarks file",
        required=True,
    )
    parser.add_argument(
        "-o", "--output", type=_output_file, help="Output bookmarks file", required=False
    )
    parser.add_argument(
        "-O",
        "--output-format",
        help="The bookmark format of the output bookmarks file",
        required=True,
    )

    args = parser.parse_args(argv)
    return parser, args


def _parse_bookmark_format(bookmark_type: str) -> tuple[Converter, BaseFormat]:
    try:
        converter, format_ = bookmark_type.split("/", 1)
    except ValueError:
        raise ValueError(f"Invalid bookmark format: {bookmark_type}")
    converter = converter.lower()
    if converter not in CONVERTER_NAMES:
        raise ValueError(f"Unsupported bookmark converter: {converter}")

    converter = CONVERTERS.get(converter)()
    format_ = Format(format_.lower())
    if format_ not in converter.formats:
        raise ValueError(
            f"The converter '{converter.__class__.__name__}' doesn't support the format '{format_}'"
        )

    format_ = FORMATS.get(format_)
    return converter, format_


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]

    parser, args = _parse_args(argv)
    try:
        input_converter, input_format = _parse_bookmark_format(args.input_format)
        output_converter, output_format = _parse_bookmark_format(args.output_format)
    except ValueError as e:
        parser.error(str(e))

    input_file = Path(args.input)
    output_file = args.output
    if output_file is None:
        output_file = _new_file_name(input_file.parent, output_format.extension)

    try:
        bookmarks = input_format.load(input_converter, input_file)
        output_format.save(output_converter, bookmarks, output_file)
    except (DatabaseError, OperationalError):
        parser.error(f"The provided file '{input_file}' is not a valid sqlite3 database file.")
    except (AttributeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        parser.error(f"The provided file '{input_file}' is not a valid bookmarks file.")
    except Exception:
        parser.error(f"RuntimeError: An unexpected error has occurred.")

    sys.stdout.buffer.write(
        bytes(
            f"Conversion successful!\nThe converted file can be found at '{output_file}'\n",
            "utf-8",
        )
    )

    return 0
