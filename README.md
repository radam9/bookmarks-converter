# Bookmarks_Converter

---
[![image](https://img.shields.io/github/workflow/status/radam9/bookmarks_converter/build-deploy?style=flat-square)](https://github.com/radam9/bookmarks_converter)
[![image](https://img.shields.io/github/license/radam9/bookmarks_converter?style=flat-square)](https://pypi.org/project/bookmarks-converter/)
[![image](https://img.shields.io/pypi/pyversions/bookmarks-converter?style=flat-square)](https://pypi.org/project/bookmarks-converter/)


Bookmarks Converter is a package that converts the webpage bookmarks
from `DataBase`/`HTML`/`JSON` to `DataBase`/`HTML`/`JSON`.

- The Database files supported are custom sqlite database files created by the SQLAlchemy ORM model found in the [`.models.py`](/src/bookmarks_converter/models.py).

- The HTML files supported are Netscape-Bookmark files from either Chrome or Firefox. The output HTML files adhere to the firefox format.

- The JSON files supported are the Chrome `.json` bookmarks file, the Firefox `.json` bookmarks export file, and the custom json file created by this package.

To see example of the structure or layout of the `DataBase`, `HTML` or `JSON` versions supported by the packege, you can check the corresponding file in the data folder found in the [github page data](data/) or the [bookmarks_file_structure.md](bookmarks_file_structure.md).

---
### Python and OS Support
The package has been tested on Github Actions with the following OSs and Python versions:

| OS \ Python      |  `3.9`  |  `3.8`  |  `3.7`  |  `3.6`  |
| :--------------- | :-----: | :-----: | :-----: | :-----: |
| `macos-latest`   | &check; | &check; | &check; | &check; |
| `ubuntu-latest`  | &check; | &check; | &check; | &check; |
| `windows-latest` | &check; | &check; | &check; | &check; |


---
### Dependencies
The package relies on the following libraries:
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/): used to parse the HTML files.
- [SQLAlchemy](https://www.sqlalchemy.org/): used to create and manager the database files.

---
### Install
Bookmarks Converter is available on [PYPI](https://pypi.org/project/bookmarks-converter/)
```bash
python -m pip install bookmarks-converter
```

---
### Test
To test the package you will need to clone the [git repository](https://github.com/radam9/bookmarks_converter).

```bash
# Cloning with HTTPS
git clone https://github.com/radam9/bookmarks_converter.git

# Cloning with SSH
git clone git@github.com:radam9/bookmarks_converter.git
```
then you create and install the dependencies using [`Poetry`](https://python-poetry.org/).

```bash
# navigate to repo's folder
cd bookmarks_converter
# install the dependencies
poetry install
# run the tests
poetry run pytest
```

---
### Usage
```python
from bookmarks_converter import BookmarksConverter

# initialize the class passing in the path to the bookmarks file to convert
bookmarks = BookmarksConverter("/path/to/bookmarks_file")

# parse the file passing the format of the source file; "db", "html" or "json"
bookmarks.parse("html")

# convert the bookmarks to the desired format by passing the fomrat as a string; "db", "html", or "json"
bookmarks.convert("json")

# at this point the converted bookmarks are stored in the 'bookmarks' attribute.
# which can be used directly or exported to a file.
bookmarks.save()
```

---
### License
[MIT License](LICENSE)