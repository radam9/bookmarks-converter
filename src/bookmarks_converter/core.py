"""Bookmarks Converter, is a package that converts the webpage bookmarks
from DB/HTML/JSON to DB/HTML/JSON.

The DB files supported are custom (self made) sqlite database files,
to see the exact format of the database you can check the .db file found
in the data folder.

The HTML files supported are Netscape-Bookmark files from either Chrome or
Firefox. The output HTML files adhere to the firefox format.

The JSON files supported are the Chrome bookmarks file, the Firefox
.json bookmarks export file, and the custom json file created by this package"""


import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Bookmark, HTMLBookmark, JSONBookmark


class DBMixin:
    """Mixing containing all the DB related functions."""

    def _parse_db(self):
        """Import the DB bookmarks file into self._tree as an object."""
        database_path = f"sqlite:///{str(self.filepath)}"
        engine = create_engine(database_path, encoding="utf-8")
        Session = sessionmaker(bind=engine)
        session = Session()
        self._tree = session.query(Bookmark).get(1)

    def _convert_to_db(self):
        """Convert the imported bookmarks to database objects."""
        self.bookmarks = []
        self._stack = [self._tree]

        while self._stack:
            self._stack_item = self._stack.pop()
            self._iterate_folder_db()

    def _iterate_folder_db(self):
        """Iterate through each item in the hierarchy tree and create
        a database object, appending any folders that contain children to
        the stack for further processing."""
        folder = self._stack_item._convert_folder_to_db()
        self.bookmarks.append(folder)
        parent_id = folder.id
        for child in self._stack_item:
            child.parent_id = parent_id
            if child.type == "folder":
                if child.children:
                    self._stack.append(child)
                else:
                    folder = child._convert_folder_to_db()
                    self.bookmarks.append(folder)
            else:
                url = child._convert_url_to_db()
                self.bookmarks.append(url)

    def _save_to_db(self):
        """Function to export the bookmarks as SQLite3 DB."""
        database_path = f"sqlite:///{str(self.output_filepath.with_suffix('.db'))}"
        engine = create_engine(database_path, encoding="utf-8")
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.commit()
        session.bulk_save_objects(self.bookmarks)
        session.commit()


class HTMLMixin:
    """Mixing containing all the HTML related functions."""

    def _parse_html(self):
        """Imports the HTML Bookmarks file into self._tree as a modified soup
        object using the TreeBuilder class HTMLBookmark, which adds property
        access to the html attributes of the soup object."""
        self.format_html_file(self.filepath, self.temp_filepath)
        with open(self.temp_filepath, "r", encoding="utf-8") as file_:
            soup = BeautifulSoup(
                markup=file_,
                features="html.parser",
                from_encoding="Utf-8",
                element_classes={Tag: HTMLBookmark},
            )
        self.temp_filepath.unlink()
        HTMLBookmark.reset_id_counter()
        tree = soup.find("h3")
        self._restructure_root(tree)
        self._add_index()

    @staticmethod
    def format_html_file(filepath, output_filepath):
        """Takes in an absolute path to a HTML Bookmarks file, it creates a new
        Bookmarks file with the text "output_" prepended to the filename.
        where;
        - The main "<H1>" tag is converted to "<H3>" and acts as the root folder
        - All "<DT>" tags are removed.
        - "<H3>" acts as folders and list containers instead of "<DL>".
        - All "<H3>" and "<A>" tag's inner text are added as a "title"
        attribute within the html element.

        filepath: str
            absolute path to bookmarks html file.
        output_filepath: str
            absolute path and name for output file."""
        with open(filepath, "r", encoding="utf-8") as input_file, open(
            output_filepath, "w", encoding="utf-8"
        ) as output_file:
            # regex to select an entire H1/H3/A HTML element
            element = re.compile(r"(<(H1|H3|A))(.*?(?=>))>(.*)(<\/\2>)\n")

            for line in input_file:
                if "<DL><p>" in line:
                    continue
                line = element.sub(r'\1\3 TITLE="\4">\5', line)
                line = (
                    line.replace("<DT>", "")
                    .replace("<H1", "<H3")
                    .replace("</H1>", "")
                    .replace("</H3>", "")
                    .replace("</DL><p>\n", "</H3>")
                    .replace("\n", "")
                    .strip()
                )
                output_file.write(line)

    def _restructure_root(self, tree):
        """Restructure the root of the HTML parsed tree to allow for an easier
        processing.

        If the tree title is 'Bookmarks Menu' we need to extract the two folders
        'Bookmarks Toolbar' and 'Other Bookmarks', then insert them into the
        root folders children.

        If the tree title is 'Bookmarks' we need to extract the 'Bookmarks bar'
        folder and insert it at the beginning of the root children. Then we need
        to rename the 'Bookmarks' folder to 'Other Bookmarks'.

        tree: :class: `bs4.element.Tag`
            BeautifulSoup object containing the first <H3> tag found in the
            html file."""
        self._tree = HTMLBookmark(
            name="h3",
            attrs={
                "id": 1,
                "index": 0,
                "parent_id": 0,
                "title": "root",
                "date_added": round(time.time() * 1000),
            },
        )
        self._tree.children.append(tree)
        if tree.title == "Bookmarks Menu":
            for i, child in enumerate(tree):
                if child.title in ("Bookmarks Toolbar", "Other Bookmarks"):
                    self._tree.children.append(tree.children.pop(i))
        elif tree.title == "Bookmarks":
            tree.title = "Other Bookmarks"
            for i, child in enumerate(tree):
                if child.title == "Bookmarks bar":
                    self._tree.children.insert(0, tree.children.pop(i))
                    break

    def _convert_to_html(self):
        """Convert the imported bookmarks to HTML."""
        header = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks Menu</H1>

<DL><p>
"""
        footer = "</DL>"

        self._stack = self._tree.children[::-1]
        body = []

        while self._stack:
            self._stack_item = self._stack.pop()
            folder = self._iterate_folder_html()
            if folder:
                self._create_placeholder(body, folder)

        self.bookmarks = "".join([header, *body, footer])

    def _iterate_folder_html(self):
        """Iterate through each item in the hierarchy tree and convert it to
        HTML. If a folder has children, it is added to the stack and a
        placeholder is left in its place so it can be inserted back to its
        position after processing."""
        folder = [self._stack_item._convert_folder_to_html(), "<DL><p>\n"]
        list_end = "</DL><p>\n"
        for child in self._stack_item:
            if child.type == "folder":
                item = f"<folder{child.id}>"
                self._stack.append(child)
            else:
                item = child._convert_url_to_html()
            folder.append(item)
        folder.append(list_end)
        result = "".join(folder)
        return result

    def _create_placeholder(self, body, folder):
        placeholder = f"<folder{self._stack_item.id}>"
        if body and (placeholder in body[-1]):
            body[-1] = body[-1].replace(placeholder, folder)
        else:
            body.append(folder)

    def _save_to_html(self):
        """Export the bookmarks as HTML."""
        output_file = self.output_filepath.with_suffix(".html")
        with open(output_file, "w", encoding="utf-8") as file_:
            file_.write(self.bookmarks)


class JSONMixin:
    """Mixing containing all the JSON related functions."""

    def _parse_json(self):
        """Imports the JSON Bookmarks file into self._tree as a
        JSONBookmark object."""
        self.format_json_file(self.filepath, self.temp_filepath)
        # with object_hook the json tree is loaded as JSONBookmark object tree.
        with open(self.temp_filepath, "r", encoding="utf-8") as file_:
            self._tree = json.load(file_, object_hook=self._json_to_object)
        self.temp_filepath.unlink()
        if self._tree.source == "Chrome":
            self._add_index()

    @staticmethod
    def _json_to_object(jdict):
        """Helper function used as object_hook for json load."""
        return JSONBookmark(**jdict)

    @staticmethod
    def format_json_file(filepath, output_filepath):
        """Reads Chrome/Firefox/Bookmarkie JSON bookmarks file (at filepath),
        and modifies it to a standard format to allow for easy
        parsing/converting.
        Exporting the result to a new JSON file (output_filepath) with
        a prefix of 'output_'."""
        with open(filepath, "r", encoding="utf-8") as file_:
            tree = json.load(file_)

        if tree.get("checksum"):
            tree = {
                "name": "root",
                "id": 0,
                "index": 0,
                "parent_id": 0,
                "type": "folder",
                "date_added": 0,
                "children": list(tree.get("roots").values()),
            }
            tree["children"][1]["name"] = "Other Bookmarks"
        elif tree.get("root"):
            tree["title"] = "root"
            folders = {
                "menu": "Bookmarks Menu",
                "toolbar": "Bookmarks Toolbar",
                "unfiled": "Other Bookmarks",
                "mobile": "Mobile Bookmarks",
            }
            for child in tree.get("children"):
                child["title"] = folders[child.get("title")]

        with open(output_filepath, "w", encoding="utf-8") as file_:
            json.dump(tree, file_, ensure_ascii=False)

    def _convert_to_json(self):
        """Convert the imported bookmarks to JSON."""
        self._stack = []
        self.bookmarks = self._tree._convert_folder_to_json()
        self._stack.append((self.bookmarks, self._tree))

        while self._stack:
            self._stack_item = self._stack.pop()
            folder, node = self._stack_item
            children = folder.get("children")
            for child in node:
                if child.type == "folder":
                    item = child._convert_folder_to_json()
                    if child.children:
                        self._stack.append((item, child))
                else:
                    item = child._convert_url_to_json()
                children.append(item)

    def _save_to_json(self):
        """Function to export the bookmarks as JSON."""
        output_file = self.output_filepath.with_suffix(".json")
        with open(output_file, "w", encoding="utf-8") as file_:
            json.dump(self.bookmarks, file_, ensure_ascii=False)


class BookmarksConverter(DBMixin, HTMLMixin, JSONMixin):
    """Bookmarks Converter class that converts the bookmarks to DB/HTML/JSON,
    using Iteration and Stack.

    Usage:
    1- Instantiate a class and pass in the filepath as string or `Path` object:
        - `instance = BookmarksConverter(filepath)`.
    2- Import and Parse the bookmarks file passing the source format as a string in lower case:
        - `instance.parse("db")`, for a database file.
        - `instance.parse("html")`, for a html file.
        - `instance.parse("json")`, for a json file.
    3- Convert the data to the desired format passing the format as a lower
    case string:
        - `instance.convert("db")`, convert to database.
        - `instance.convert("html")`, convert to html.
        - `instance.convert("json")`, convert to json.
    4- At this point the bookmarks are stored in the `bookmarks` attribute
        accessible through `instance.bookmarks`.
    5- Export the bookmarks to a file using the save method `instance.save()`.

    Parameters:
    -----------
    filepath : str or Path
        path to the file to be converted using BookmarksConverter

    Attributes:
    -----------
    bookmarks : list or dict or str
        list, dict or str containing the bookmarks converted using BookmarksConverter.
        - list of database objects if converted to database
        - dict tree with bookmarks if converted to json
        - str of the tree if converted to html
    filepath : str or Path
        path to the file to be converted using BookmarksConverter
    output_filepath : Path
        path to the output file exported using `.save()` method"""

    _formats = ("db", "html", "json")

    def __init__(self, filepath):
        self._export = None
        self._format = None
        self._stack = None
        self._stack_item = None
        self._tree = None
        self.bookmarks = None
        self.filepath = Path(filepath)
        self._prepare_filepaths()

    def _prepare_filepaths(self):
        """Takes in filepath, and creates the following filepaths:

        -temp_filepath: filepath used for temporary file created by
         format_html_file() and format_json_file() methods.

        -output_filepath: output filepath used by the save_to_**(DB/HTML/JSON)
         methods to save the converted data into a file.

        If the output_file already exists, increment the number at the end of
        the output filename."""
        self.output_filepath = self.filepath.with_name(
            f"output_{self.filepath.stem}_001{self.filepath.suffix}"
        )
        while self.output_filepath.is_file():
            self._rename_outputfile()

        self.temp_filepath = self.filepath.with_name(f"temp_{self.filepath.name}")

    def _rename_outputfile(self):
        """Increments the number at the end of the output filename,
        i.e: `output_bookmarks_001.html`"""
        filename = self.output_filepath.stem.split("_")
        if filename[-1].isdigit():
            num = int(filename[-1]) + 1
            filename[-1] = f"{num:03d}"
            self.output_filepath = self.output_filepath.with_name(
                f"{'_'.join(filename)}{self.output_filepath.suffix}"
            )

    def _add_index(self):
        """Add index to each element if tree source is HTML or JSON(Chrome)"""
        stack = [self._tree]
        while stack:
            stack_item = stack.pop()
            for i, child in enumerate(stack_item, 0):
                child.index = i
                if child.type == "folder":
                    stack.append(child)

    def _dispatcher(self, method):
        if self._format.lower() not in self._formats:
            raise TypeError(
                "The format you specified does not exist, make sure its 'db', 'html' or 'json'."
            )
        getattr(self, method)()

    def parse(self, format_):
        format_.lower()
        self._format = format_
        self._dispatcher(f"_parse_{format_}")

    def convert(self, format_):
        format_ = format_.lower()
        self._format = format_
        self._export = format_
        self._dispatcher(f"_convert_to_{format_}")

    def save(self):
        if self._export is None:
            raise RuntimeError(
                "The bookmarks attribute is empty, you have to 'convert' the bookmarks before exporting them using 'save'."
            )
        self._dispatcher(f"_save_to_{self._export}")
