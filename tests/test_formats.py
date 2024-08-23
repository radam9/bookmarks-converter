import datetime

from conftest import DATA_DIR

from bookmarks_converter.formats import Format, _new_file_name


def test_new_file_name():
    path = DATA_DIR
    extension = Format.DB
    result = _new_file_name(path, extension)
    assert result.suffix == ("." + extension)
    now = datetime.datetime.now()
    name, date, time = str(result.stem).split("-")
    assert name == "bookmarks"
    assert date == now.strftime("%Y%m%d")
    assert time.isdigit()
