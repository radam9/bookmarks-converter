import json
import random
import string
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
    Bookmark,
    Folder,
    HTMLBookmark,
    SpecialFolder,
    Url,
)
from bookmarks_converter.util import format_html, indent_html

MOZILLA_GUID_LENGTH = 12
MOZILLA_PLACE_CONST = "text/x-moz-place"
MOZILLA_CONTAINER_CONST = "text/x-moz-place-container"
MOZILLA_SEPARATOR_CONST = "text/x-moz-place-separator"
MOZILLA_MENU_FOLDER_HTML_TITLE = "Bookmarks Menu"
MOZILLA_TOOLBAR_FOLDER_HTML_TITLE = "Bookmarks Toolbar"
MOZILLA_TOOLBAR_FOLDER_HTML_FLAG = "PERSONAL_TOOLBAR_FOLDER"
MOZILLA_OTHER_FOLDER_HTML_TITLE = "Other Bookmarks"
MOZILLA_OTHER_FOLDER_HTML_FLAG = "UNFILED_BOOKMARKS_FOLDER"
MOZILLA_ROOT_FOLDER_JSON_TITLE = ""
MOZILLA_ROOT_FOLDER_JSON_GUID = "root________"
MOZILLA_MENU_FOLDER_JSON_TITLE = "menu"
MOZILLA_MENU_FOLDER_JSON_GUID = "menu________"
MOZILLA_TOOLBAR_FOLDER_JSON_TITLE = "toolbar"
MOZILLA_TOOLBAR_FOLDER_JSON_GUID = "toolbar_____"
MOZILLA_OTHER_FOLDER_JSON_TITLE = "unfiled"
MOZILLA_OTHER_FOLDER_JSON_GUID = "unfiled_____"
MOZILLA_MOBILE_FOLDER_JSON_TITLE = "mobile"
MOZILLA_MOBILE_FOLDER_JSON_GUID = "mobile______"

MOZILLA_HTML_HEADER = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'none'; img-src data: *; object-src 'none'"></meta>
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks Menu</H1>

<DL><p>
"""


class FolderRoot(Enum):
    placesRoot = SpecialFolder.ROOT
    bookmarksMenuFolder = SpecialFolder.MENU
    toolbarFolder = SpecialFolder.TOOLBAR
    unfiledBookmarksFolder = SpecialFolder.OTHER
    mobileFolder = SpecialFolder.MOBILE


class Firefox(Converter):
    formats = (Format.HTML, Format.JSON)

    def as_html(self, tree: Bookmark) -> str:
        """Converts bookmark object tree to HTML."""
        footer = "</DL>\n"

        # Firefox doesn't export mobile bookmarks in the HTML export.
        for i, child in enumerate(tree.children):
            if child.special_folder == SpecialFolder.MOBILE:
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
        return indent_html("".join([MOZILLA_HTML_HEADER, *body, footer]))

    def _iterate_folder_html(self, node: Folder) -> str:
        """Iterate through each item in the hierarchy tree and convert it to
        HTML. If a folder has children, it is added to the stack and a
        placeholder is left in its place, so it can be inserted back to its
        position after processing."""
        if node.special_folder == SpecialFolder.MENU:
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
        folder_html = f'<DT><H3 ADD_DATE="{int(folder.date_added / 1000_000)}"'

        if folder.date_modified:
            folder_html += f' LAST_MODIFIED="{int(folder.date_modified / 1000_000)}"'

        title = folder.title
        if folder.special_folder == SpecialFolder.TOOLBAR:
            folder_html += f' {MOZILLA_TOOLBAR_FOLDER_HTML_FLAG}="true"'
            title = MOZILLA_TOOLBAR_FOLDER_HTML_TITLE
        elif folder.special_folder == SpecialFolder.OTHER:
            folder_html += f' {MOZILLA_OTHER_FOLDER_HTML_FLAG}="true"'
            title = MOZILLA_OTHER_FOLDER_HTML_TITLE

        folder_html += f">{escape(title)}</H3>\n"
        return folder_html

    @staticmethod
    def _url_as_html(url: Bookmark | Url) -> str:
        url_html = f'<DT><A HREF="{url.url}" ADD_DATE="{int(url.date_added / 1000_000)}"'

        if url.date_modified:
            url_html += f' LAST_MODIFIED="{int(url.date_modified / 1000_000)}"'

        if url.icon_uri:
            url_html += f' ICON_URI="{url.icon_uri}"'

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

        We need to extract the two folders 'Bookmarks Toolbar' and 'Other Bookmarks',
        then insert them into the root folders children.

        tree: :class: `bs4.element.Tag`
            BeautifulSoup object containing the first <H3> tag found in the
            html file.
        """
        new_tree = HTMLBookmark(
            name="h3",
            attrs={
                "id": 1,
                "index": 0,
                "parent_id": 0,
                "title": "",
                "date_added": round(time.time() * 1000),
            },
        )
        new_tree.children.append(tree)
        children = []
        while tree.children:
            child = tree.children.pop(0)
            if (
                MOZILLA_TOOLBAR_FOLDER_HTML_FLAG.lower() in child.attrs
                or MOZILLA_OTHER_FOLDER_HTML_FLAG.lower() in child.attrs
            ):
                new_tree.children.append(child)
            else:
                children.append(child)

        tree.children.extend(children)
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
        if node.title == MOZILLA_MENU_FOLDER_HTML_TITLE:
            return SpecialFolder.MENU

        if (
            MOZILLA_TOOLBAR_FOLDER_HTML_FLAG.lower() in node.attrs
            or node.title == MOZILLA_TOOLBAR_FOLDER_HTML_TITLE
        ):
            return SpecialFolder.TOOLBAR

        if (
            MOZILLA_OTHER_FOLDER_HTML_FLAG.lower() in node.attrs
            or node.title == MOZILLA_OTHER_FOLDER_HTML_TITLE
        ):
            return SpecialFolder.OTHER

    def as_json(self, tree: Bookmark) -> dict:
        """Convert a Bookmarks tree to JSON."""
        bookmarks = self._folder_as_json(tree)
        stack = [(bookmarks, tree)]

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

    def _folder_as_json(self, folder: Bookmark | Folder) -> dict:
        folder_json = {
            "guid": self._ensure_mozilla_guid(folder.guid),
            "title": folder.title,
            "index": folder.index,
            "dateAdded": folder.date_added,
            "lastModified": folder.date_modified,
            "id": folder.id,
            "typeCode": 2,
            "type": MOZILLA_CONTAINER_CONST,
        }

        if folder.special_folder:
            folder_json["root"] = FolderRoot(folder.special_folder).name

            if folder.special_folder == SpecialFolder.ROOT:
                folder_json["title"] = MOZILLA_ROOT_FOLDER_JSON_TITLE
                folder_json["guid"] = MOZILLA_ROOT_FOLDER_JSON_GUID
            elif folder.special_folder == SpecialFolder.MENU:
                folder_json["title"] = MOZILLA_MENU_FOLDER_JSON_TITLE
                folder_json["guid"] = MOZILLA_MENU_FOLDER_JSON_GUID
            elif folder.special_folder == SpecialFolder.TOOLBAR:
                folder_json["title"] = MOZILLA_TOOLBAR_FOLDER_JSON_TITLE
                folder_json["guid"] = MOZILLA_TOOLBAR_FOLDER_JSON_GUID
            elif folder.special_folder == SpecialFolder.OTHER:
                folder_json["title"] = MOZILLA_OTHER_FOLDER_JSON_TITLE
                folder_json["guid"] = MOZILLA_OTHER_FOLDER_JSON_GUID
            elif folder.special_folder == SpecialFolder.MOBILE:
                folder_json["title"] = MOZILLA_MOBILE_FOLDER_JSON_TITLE
                folder_json["guid"] = MOZILLA_MOBILE_FOLDER_JSON_GUID

        # add the children at the end to keep the same order as firefox json file.
        folder_json["children"] = []

        return folder_json

    def _url_as_json(self, url: Bookmark | Url) -> dict:
        url_json = {
            "guid": self._ensure_mozilla_guid(url.guid),
            "title": url.title,
            "index": url.index,
            "dateAdded": url.date_added,
            "lastModified": url.date_modified,
            "id": url.id,
            "typeCode": 1,
        }

        if url.icon_uri_is_set():
            url_json["iconuri"] = url.icon_uri

        # add url and type at the end to keep the same order as firefox json file.
        url_json.update({"type": MOZILLA_PLACE_CONST, "uri": url.url})

        return url_json

    @staticmethod
    def _ensure_mozilla_guid(guid: str) -> str:
        """Ensure that the guid follows the mozilla firefox guid spec.
        The code for the guid generation in the firefox source code can be found in:
        - /services/sync/modules/util.sys.mjs `makeGUID()`
        - https://searchfox.org/mozilla-central/source/services/sync/modules/util.sys.mjs#204
        """
        if len(guid) == MOZILLA_GUID_LENGTH:
            return guid

        return "".join(
            random.choice(string.ascii_letters + string.digits + "-_")
            for _ in range(MOZILLA_GUID_LENGTH)
        )

    def from_json(self, filepath: Path) -> Bookmark:
        """Imports the JSON Bookmarks file as a Bookmark tree."""
        with filepath.open("r", encoding="utf-8") as file:
            # use the object_hook to load the json tree as a Bookmark tree.
            tree = self._json_to_object(json.load(file))
        return tree

    def _json_to_object(self, jdict: dict) -> Bookmark:
        """Convert json tree into a Bookmark tree."""
        bookmarks = self._json_as_folder(jdict)
        stack = [(bookmarks, jdict)]

        while stack:
            folder, node = stack.pop()
            children = folder.children
            for child in node.get("children"):
                if child.get("type") == MOZILLA_CONTAINER_CONST:
                    item = self._json_as_folder(child)
                    if child.get("children"):
                        stack.append((item, child))
                elif child.get("type") == MOZILLA_PLACE_CONST:
                    item = self._json_as_url(child)
                elif child.get("type") == MOZILLA_SEPARATOR_CONST:
                    continue

                children.append(item)

        return bookmarks

    @staticmethod
    def _json_as_folder(jdict: dict) -> Folder:
        kwargs = {
            "id": int(jdict.pop("id")),
            "index": jdict.pop("index"),
            "title": jdict.pop("title", None),
            "date_added": int(jdict.pop("dateAdded", 0)),
            "date_modified": int(jdict.pop("lastModified", 0)),
            "guid": jdict.pop("guid", str(uuid4())),
            "children": [],
        }
        special_folder = jdict.pop("root", "")
        if special_folder:
            kwargs["special_folder"] = FolderRoot[special_folder].value

        return Folder(**kwargs)

    @staticmethod
    def _json_as_url(jdict: dict) -> Url:
        kwargs = {
            "id": int(jdict.pop("id")),
            "index": jdict.pop("index"),
            "title": jdict.pop("title", None),
            "date_added": int(jdict.pop("dateAdded", 0)),
            "date_modified": int(jdict.pop("lastModified", 0)),
            "guid": jdict.pop("guid", str(uuid4())),
            "url": jdict.pop("uri"),
            "icon": jdict.pop("icon", ""),
            "icon_uri": jdict.pop("iconuri", ""),
            "tags": jdict.pop("tags", []),
        }

        return Url(**kwargs)
