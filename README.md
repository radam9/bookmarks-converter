# Bookmarks Converter

---
[![image](https://img.shields.io/github/actions/workflow/status/radam9/bookmarks-converter/build-deploy.yml?branch=main&style=flat-square)](https://github.com/radam9/bookmarks-converter)
[![image](https://img.shields.io/github/license/radam9/bookmarks-converter?style=flat-square)](https://pypi.org/project/bookmarks-converter/)
[![image](https://img.shields.io/pypi/pyversions/bookmarks-converter?style=flat-square)](https://pypi.org/project/bookmarks-converter/)


BookmarksConverter is a package that converts browser bookmark files, usable as a [`module`](#usage-as-module) or as a [CLI](#usage-as-cli).

BookmarksConverter supports the converters below:

- Bookmarkie (custom formats)
- Chrome/Chromium
- Firefox

The converters can import and export bookmarks from and to the formats listed below:

- Bookmarkie: `DB`, `HTML`, `JSON`
- Chrome/Chromium: `HTML`, `JSON`
- Firefox: `HTML`, `JSON`

Notes:

- Supports Netscape-Bookmark format for `HTML` files
- The exported `HTML` files are compatible with all browsers.
- Custom `DB` files are powered by SQLAlchemy ORM (see [`models.py`](/src/bookmarks_converter/models.py)).
- Chrome/Chromium `JSON` files cannot be directly imported but can be placed in the appropriate location (see [bookmarks_file_structure.md - Chrome/Chromium - b. JSON](./bookmarks_file_structure.md#b-json)).
- For examples of supported `DB`, `HTML`, or `JSON` structures and formats, refer to the [test resources](tests/resources) or [bookmarks_file_structure.md](bookmarks_file_structure.md).
- Custom `DB` and `JSON` formats by BookmarksConverter are not browser-importable.

---
## Table of Contents
  - [Table of Contents](#table-of-contents)
    - [Python and OS Support](#python-and-os-support)
    - [Dependencies](#dependencies)
    - [Install](#install)
    - [Test](#test)
    - [Usage as Module](#usage-as-module)
    - [Usage as CLI](#usage-as-cli)
    - [License](#license)
---
### Python and OS Support
The package has been tested on GitHub Actions with the following OSs and Python versions:

| OS \ Python      | `3.11`  | `3.12`  | `3.13`  | `3.14`  |
|:-----------------|:-------:|:-------:|:-------:|:-------:|
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
To test the package you will need to clone the [git repository](https://github.com/radam9/bookmarks-converter).

```bash
# Cloning with HTTPS
git clone https://github.com/radam9/bookmarks-converter.git

# Cloning with SSH
git clone git@github.com:radam9/bookmarks-converter.git
```
then you create and install the dependencies using [`Poetry`](https://python-poetry.org/).

```bash
# navigate to repo's folder
cd bookmarks-converter
# install the dependencies
poetry install
# run the tests
poetry run pytest
```

---
### Usage as Module
```python
from pathlib import Path
from bookmarks_converter import Chrome, Firefox
from bookmarks_converter.formats import save_json

# initialize the converter
firefox = Firefox()
chrome = Chrome()

# import the bookmarks
input_file = Path("/path/to/input.html")
content = firefox.from_html(input_file)

# convert to desired format
output_file = Path("/path/to/output.json")
bookmarks = chrome.as_json(content)

# finally save the bookmarks
# there are some helper files that could be useful for saving to files
save_json(bookmarks, output_file)
```

---
### Usage as CLI

`bookmarks-converter` cli can be installed inside a virtual environment or using [pipx](https://github.com/pypa/pipx).
```bash
# bookmarks-converter usages:
# example 1
bookmarks-converter -i ./input_bookmarks.db --input-format 'bookmarkie/db' --output-format 'chrome/html'

# example 2
bookmarks-converter -i ./some_bookmarks.html -I 'chrome/html' -o ./output_bookmarks.json -O 'firefox/json'
```

The help message:
```bash
# use -h for to show the help message (shown in the code block below)
$ bookmarks-converter --help

usage: bookmarks-converter [-h] [-V] -i INPUT -I INPUT_FORMAT [-o OUTPUT] -O OUTPUT_FORMAT

Convert your browser bookmarks file.

The bookmark format is composed of two parts separated by a slash: [CONVERTER]/[FORMAT], ex. 'firefox/html'
With the converter being one of the available converters: ('bookmarkie', 'chrome', 'firefox')
And the format being one of the available formats: ('db', 'html', 'json')

Example Usage:
    bookmarks-converter -i ./input_bookmarks.db --input-format 'bookmarkie/db' --output-format 'chrome/html'
    bookmarks-converter -i ./some_bookmarks.html -I 'chrome/html' -o ./output_bookmarks.json -O 'firefox/json'
    

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -i INPUT, --input INPUT
                        Input bookmarks file
  -I INPUT_FORMAT, --input-format INPUT_FORMAT
                        The bookmark format of the input bookmarks file
  -o OUTPUT, --output OUTPUT
                        Output bookmarks file
  -O OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        The bookmark format of the output bookmarks file
```

---
### License
[MIT License](LICENSE)
