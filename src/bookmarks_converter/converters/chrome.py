import json
import time
from enum import Enum
from html import escape
from pathlib import Path
from uuid import uuid4

from bs4 import BeautifulSoup, Tag

from bookmarks_converter.converters.converter import Converter
from bookmarks_converter.formats import Format
from bookmarks_converter.models import (
    TYPE_FOLDER,
    TYPE_URL,
    Bookmark,
    Folder,
    HTMLBookmark,
    SpecialFolder,
    Url,
)
from bookmarks_converter.util import format_html, indent_html

# chrome json bookmarks have timestamps as microseconds since January 1, 1601, rather than seconds
# since January 1, 1970. The constant below is the offset in milliseconds between the two dates.
CHROME_EPOCH_CONSTANT = 11644473600000000


CHROME_BOOKMARK_BAR_FOLDER_HTML_FLAG = "PERSONAL_TOOLBAR_FOLDER"
CHROME_BOOKMARK_BAR_FOLDER_TITLE = "Bookmarks bar"
CHROME_BOOKMARK_OTHER_FOLDER_TITLE = "Other bookmarks"
CHROME_BOOKMARK_MOBILE_FOLDER_TITLE = "Mobile bookmarks"

CHROME_HTML_HEADER = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
"""


class FolderRoot(Enum):
    root = SpecialFolder.ROOT
    Bookmarks_bar = SpecialFolder.TOOLBAR
    Other_bookmarks = SpecialFolder.OTHER
    Mobile_bookmarks = SpecialFolder.MOBILE


class Chrome(Converter):
    formats = (Format.HTML, Format.JSON)

    def as_html(self, tree: Bookmark) -> str:
        """Converts bookmark object tree to HTML."""
        footer = "</DL><p>\n"

        # Chrome doesn't export Menu bookmarks in the HTML export.
        for i, child in enumerate(tree.children):
            if child.special_folder == SpecialFolder.MENU:
                tree.children.pop(i)

        self._stack = tree.children[::-1]
        body = []

        while self._stack:
            stack_item = self._stack.pop()
            folder = self._iterate_folder_html(stack_item)
            if not folder:
                continue

            self._create_placeholder(body, folder, stack_item)

        self._stack = None
        return indent_html("".join([CHROME_HTML_HEADER, *body, footer]))

    def _iterate_folder_html(self, node: Folder) -> str:
        """Iterate through each item in the hierarchy tree and convert it to
        HTML. If a folder has children, it is added to the stack and a
        placeholder is left in its place, so it can be inserted back to its
        position after processing."""
        if node.special_folder in (SpecialFolder.OTHER, SpecialFolder.MOBILE):
            folder = []
            list_end = ""
        else:
            folder = [self._folder_as_html(node), "<DL><p>\n"]
            list_end = "</DL><p>\n"

        for child in node.children:
            if isinstance(child, Folder):
                item = f"<folder{child.id}>"
                self._stack.append(child)
            else:
                item = self._url_as_html(child)
            folder.append(item)
        folder.append(list_end)
        result = "".join(folder)
        return result

    @staticmethod
    def _create_placeholder(body, folder, stack_item):
        placeholder = f"<folder{stack_item.id}>"
        if body and (placeholder in body[-1]):
            body[-1] = body[-1].replace(placeholder, folder)
        else:
            body.append(folder)

    @staticmethod
    def _folder_as_html(folder: Bookmark | Folder) -> str:
        folder_html = f'<DT><H3 ADD_DATE="{int(folder.date_added/1000_000)}" LAST_MODIFIED="{int(folder.date_modified/1000_000)}"'
        title = folder.title

        if folder.special_folder == SpecialFolder.TOOLBAR:
            folder_html += f' {CHROME_BOOKMARK_BAR_FOLDER_HTML_FLAG}="true"'
            title = CHROME_BOOKMARK_BAR_FOLDER_TITLE

        folder_html += f">{escape(title)}</H3>\n"
        return folder_html

    @staticmethod
    def _url_as_html(url: Bookmark | Url) -> str:
        url_html = f'<DT><A HREF="{url.url}" ADD_DATE="{int(url.date_added/1000_000)}"'

        if url.icon:
            url_html += f' ICON="{url.icon}"'

        url_html += f">{escape(url.title)}</A>\n"
        return url_html

    def from_html(self, filepath: Path) -> Bookmark:
        """Imports the HTML Bookmarks file as a Bookmark tree."""
        soup = BeautifulSoup(
            markup=format_html(filepath),
            features="html.parser",
            element_classes={Tag: HTMLBookmark},
        )
        HTMLBookmark.reset_id_counter()
        tree = soup.find("h3")
        tree = self._restructure_root(tree)
        tree = self._convert_html_to_bookmarks(tree)
        return tree

    @staticmethod
    def _restructure_root(tree: BeautifulSoup) -> HTMLBookmark:
        """Restructure the root of the HTML parsed tree to allow for an easier
        processing.

        We need to extract the 'Bookmarks bar' folder and insert it at
        the beginning of the root children.
        Then we need to rename the 'Bookmarks' folder to 'Other Bookmarks'.

        tree: :class: `bs4.element.Tag`
            BeautifulSoup object containing the first <H3> tag found in the
            html file."""
        new_tree = HTMLBookmark(
            name="h3",
            attrs={
                "id": 1,
                "index": 0,
                "parent_id": 0,
                "title": "root",
                "date_added": round(time.time() * 1000),
            },
        )
        new_tree.children.append(tree)
        tree.title = CHROME_BOOKMARK_OTHER_FOLDER_TITLE
        for i, child in enumerate(tree):
            if child.title == CHROME_BOOKMARK_BAR_FOLDER_TITLE:
                new_tree.children.insert(0, tree.children.pop(i))
                break
        return new_tree

    def _convert_html_to_bookmarks(self, tree: HTMLBookmark) -> Bookmark:
        """Converts an HTMLBookmark object into a Bookmark object.
        It will add the index value of each item while traversing the tree."""
        root = tree._as_folder(index=0)
        root.special_folder = SpecialFolder.ROOT

        stack = [(root, tree.children)]

        while stack:
            folder, node = stack.pop()
            children = folder.children
            for i, child in enumerate(node, 0):
                if child.type == TYPE_FOLDER:
                    item = child._as_folder(index=i)
                    special_folder = self._get_html_special_folder(child)
                    if special_folder:
                        item.special_folder = special_folder
                    if child.children:
                        stack.append((item, child))
                else:
                    item = child._as_url(index=i)
                children.append(item)
        return root

    @staticmethod
    def _get_html_special_folder(node: HTMLBookmark) -> SpecialFolder | None:
        if (
            CHROME_BOOKMARK_BAR_FOLDER_HTML_FLAG.lower() in node.attrs
            or node.title == CHROME_BOOKMARK_BAR_FOLDER_TITLE
        ):
            return SpecialFolder.TOOLBAR

        if node.title == CHROME_BOOKMARK_OTHER_FOLDER_TITLE:
            return SpecialFolder.OTHER

    def as_json(self, tree: Bookmark) -> dict:
        """Convert a Bookmarks tree to JSON.
        Chrome supports three folders in the root of the bookmarks, those are:
        'bookmarks_bar', 'other', and 'synced'.
        Any other bookmarks in the root node are ignored."""
        roots = {}

        for child in tree.children:
            # chrome doesn't support urls in the root node's children.
            if isinstance(child, Url):
                continue

            # skip Menu folder as it is not supported by chrome bookmarks.
            if child.special_folder == SpecialFolder.MENU:
                continue
            elif child.special_folder == SpecialFolder.TOOLBAR:
                child.title = CHROME_BOOKMARK_BAR_FOLDER_TITLE
                roots["bookmark_bar"] = self._iterate_folder_json(child)
            elif child.special_folder == SpecialFolder.OTHER:
                child.title = CHROME_BOOKMARK_OTHER_FOLDER_TITLE
                roots["other"] = self._iterate_folder_json(child)
            elif child.special_folder == SpecialFolder.MOBILE:
                child.title = CHROME_BOOKMARK_MOBILE_FOLDER_TITLE
                roots["synced"] = self._iterate_folder_json(child)

        result = {"roots": roots, "version": 1}

        return result

    def _iterate_folder_json(self, folder: Folder) -> dict:
        bookmarks = self._folder_as_json(folder)
        stack = [(bookmarks, folder)]
        while stack:
            folder, node = stack.pop()
            children = folder.get("children")
            for child in node.children:
                if isinstance(child, Folder):
                    item = self._folder_as_json(child)
                    if child.children:
                        stack.append((item, child))
                else:
                    item = self._url_as_json(child)
                children.append(item)
        return bookmarks

    @staticmethod
    def _folder_as_json(folder: Folder) -> dict:
        return {
            "children": [],
            "date_added": str(as_chrome_timestamp(folder.date_added)),
            "date_last_used": "0",
            "date_modified": str(as_chrome_timestamp(folder.date_modified)),
            "guid": folder.guid,
            "id": str(folder.id),
            "name": folder.title,
            "type": "folder",
        }

    @staticmethod
    def _url_as_json(url: Url) -> dict:
        return {
            "date_added": str(as_chrome_timestamp(url.date_added)),
            "date_last_used": "0",
            "guid": url.guid,
            "id": str(url.id),
            "name": url.title,
            "type": "url",
            "url": url.url,
        }

    def from_json(self, filepath: Path) -> Bookmark:
        """Imports the JSON Bookmarks file as a Bookmark tree."""
        with filepath.open(mode="r", encoding="utf-8") as file:
            # use the object_hook to load the json tree as a Bookmark tree.
            tree = json.load(file, object_hook=self._json_to_object)
        self._add_index(tree)
        return tree

    @staticmethod
    def _json_to_object(jdict: dict):
        """Helper function used as object_hook for json load."""

        # re-organize the root of the chrome bookmarks.
        if "bookmark_bar" in jdict or "other" in jdict or "synced" in jdict:
            return Folder(
                id=0,
                index=0,
                title="root",
                special_folder=SpecialFolder.ROOT,
                date_added=0,
                children=list(jdict.values()),
                guid=str(uuid4()),
                date_modified=int(jdict.get("date_modified", 0)),
            )

        # if we reach the root, return the root folder contents.
        if "roots" in jdict:
            return jdict["roots"]

        # Chrome has two fields in their json file `meta_info` and `unsynced_meta_info`.
        # We currently don't support these fields so we ignore them.
        if "id" not in jdict:
            return

        title = jdict.pop("name", None)
        kwargs = {
            "id": int(jdict.pop("id")),
            "index": jdict.pop("index", None),
            "title": title,
            "date_added": from_chrome_timestamp(int(jdict.pop("date_added", 0))),
            "date_modified": from_chrome_timestamp(int(jdict.pop("date_modified", 0))),
            "guid": jdict.pop("guid", str(uuid4())),
        }

        type_ = jdict.pop("type")
        if type_ == TYPE_FOLDER:
            kwargs["children"] = jdict.pop("children", [])
            if title in (
                CHROME_BOOKMARK_BAR_FOLDER_TITLE,
                CHROME_BOOKMARK_OTHER_FOLDER_TITLE,
                CHROME_BOOKMARK_MOBILE_FOLDER_TITLE,
            ):
                title = title.replace(" ", "_")
                kwargs["special_folder"] = FolderRoot[title].value
            return Folder(**kwargs)
        elif type_ == TYPE_URL:
            kwargs["url"] = jdict.pop("url", None)
            kwargs["icon"] = jdict.pop("icon", "")
            kwargs["icon_uri"] = jdict.pop("iconuri", "")
            kwargs["tags"] = jdict.pop("tags", [])
            return Url(**kwargs)
        else:
            raise NotImplementedError(f"Unsupported type {type_}")

    @staticmethod
    def _add_index(tree: Bookmark):
        """Add index to each Bookmark element from a json parsed file"""
        stack = [tree]
        while stack:
            node = stack.pop()
            for i, child in enumerate(node.children, 0):
                child.index = i
                if isinstance(child, Folder):
                    stack.append(child)


def as_chrome_timestamp(timestamp: int) -> int:
    if timestamp == 0:
        return 0
    return timestamp + CHROME_EPOCH_CONSTANT


def from_chrome_timestamp(timestamp: int) -> int:
    if timestamp == 0:
        return 0
    return timestamp - CHROME_EPOCH_CONSTANT
