import argparse
from pathlib import Path

import bookmarks_converter


def _get_version():
    """Get bookmarks-converter version."""
    try:
        import importlib.metadata as importlib_metadata
    except ModuleNotFoundError:
        import importlib_metadata

    return importlib_metadata.version("bookmarks-converter")


def _file(file_path):
    """Check that file exists at the given path."""
    file_path = Path(file_path)

    if not file_path.is_file():
        raise argparse.ArgumentTypeError(
            f"Could not find a file at the given file_path: '{file_path}'"
        )
    return file_path


def main(argv=None):
    parser = argparse.ArgumentParser()

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
        help="Format of the input bookmarks file.",
    )
    parser.add_argument(
        "output_format",
        choices=("db", "html", "json"),
        help="Format of the output bookmarks file.",
    )
    parser.add_argument(
        "file_path", type=_file, help="Path to bookmarks file to convert."
    )

    args = parser.parse_args(argv)
    print(vars(args))

    return 0
