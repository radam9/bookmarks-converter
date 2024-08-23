import json
import time
from enum import Enum
from html import escape
from pathlib import Path
from uuid import UUID, uuid4

from bs4 import BeautifulSoup, Tag
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from bookmarks_converter.converters.converter import Converter
from bookmarks_converter.formats import Format
from bookmarks_converter.models import (
    TYPE_FOLDER,
    TYPE_URL,
    Bookmark,
    DBBookmark,
    DBFolder,
    DBUrl,
    Folder,
    HTMLBookmark,
    SpecialFolder,
    Url,
)
from bookmarks_converter.util import format_html, indent_html

BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_HTML_FLAG = "PERSONAL_TOOLBAR_FOLDER"
BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_HTML_FLAG = "UNFILED_BOOKMARKS_FOLDER"
BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_HTML_FLAG = "MOBILE_BOOKMARKS_FOLDER"
BOOKMARKIE_BOOKMARKS_ROOT_FOLDER_TITLE = "root"
BOOKMARKIE_BOOKMARKS_MENU_FOLDER_TITLE = "Bookmarks Menu"
BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE = "Bookmarks Toolbar"
BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE = "Other Bookmarks"
BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE = "Mobile Bookmarks"

BOOKMARKIE_SPECIAL_FOLDER_TO_TITLE = {
    SpecialFolder.ROOT: BOOKMARKIE_BOOKMARKS_ROOT_FOLDER_TITLE,
    SpecialFolder.MENU: BOOKMARKIE_BOOKMARKS_MENU_FOLDER_TITLE,
    SpecialFolder.TOOLBAR: BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE,
    SpecialFolder.OTHER: BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE,
    SpecialFolder.MOBILE: BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE,
}

BOOKMARKIE_HTML_HEADER = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
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
    root = SpecialFolder.ROOT
    menu = SpecialFolder.MENU
    toolbar = SpecialFolder.TOOLBAR
    other = SpecialFolder.OTHER
    mobile = SpecialFolder.MOBILE


class Bookmarkie(Converter):
    formats = (Format.DB, Format.HTML, Format.JSON)

    def as_db(self, tree: Bookmark) -> DBBookmark:
        """Convert Bookmarks tree to DBBookmark."""
        return self._convert_to_db(tree)

    def _convert_to_db(self, tree: Bookmark) -> DBBookmark:
        bookmarks = self._folder_as_dbfolder(tree, 0)
        stack = [(bookmarks, tree)]

        while stack:
            folder, node = stack.pop()
            for child in node.children:
                if isinstance(child, Folder):
                    item = self._folder_as_dbfolder(child, folder.id)
                    if child.children:
                        stack.append((item, child))
                else:
                    item = self._url_as_dburl(child, folder.id)
                folder.children.append(item)
        return bookmarks

    @staticmethod
    def _folder_as_dbfolder(folder: [Folder], parent_id: int) -> DBFolder:
        kwargs = {
            "_id": folder.id,
            "guid": folder.guid,
            "index": folder.index,
            "parent_id": parent_id,
            "title": folder.title,
            "date_added": folder.date_added,
            "date_modified": folder.date_modified,
        }
        if folder.special_folder:
            kwargs["special_folder"] = folder.special_folder.value

        return DBFolder(**kwargs)

    @staticmethod
    def _url_as_dburl(url: [Url], parent_id: int) -> DBUrl:
        return DBUrl(
            _id=url.id,
            guid=url.guid,
            index=url.index,
            parent_id=parent_id,
            title=url.title,
            date_added=url.date_added,
            date_modified=url.date_modified,
            url=url.url,
            icon=url.icon,
            icon_uri=url.icon_uri,
            tags=",".join(url.tags),
        )

    def from_db(self, filepath: Path) -> Bookmark:
        """Import the sqlite3 DB bookmarks file as a Bookmark tree."""
        database_path = f"sqlite:///{str(filepath)}"
        engine = create_engine(database_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        bookmarks = session.scalars(
            select(DBFolder).filter_by(special_folder=SpecialFolder.ROOT.value)
        ).first()
        return self._convert_db_to_bookmarks(bookmarks)

    def _convert_db_to_bookmarks(self, tree: [DBBookmark]) -> Bookmark:
        """Converts a DBBookmark tree into a Bookmark tree."""
        bookmarks = self._dbfolder_as_folder(tree)
        stack = [(bookmarks, tree)]

        while stack:
            folder, node = stack.pop()
            for child in node.children:
                if isinstance(child, DBFolder):
                    item = self._dbfolder_as_folder(child)
                    if child.children:
                        stack.append((item, child))
                else:
                    item = self._dburl_as_url(child)
                folder.children.append(item)
        return bookmarks

    @staticmethod
    def _dbfolder_as_folder(folder: [DBFolder]) -> Bookmark:
        kwargs = {
            "id": folder.id,
            "guid": folder.guid,
            "index": folder.index,
            "title": folder.title,
            "date_added": folder.date_added,
            "date_modified": folder.date_modified,
        }
        if folder.special_folder:
            kwargs["special_folder"] = FolderRoot[folder.special_folder].value

        return Folder(**kwargs)

    @staticmethod
    def _dburl_as_url(url: DBUrl) -> Bookmark:
        tags = []
        if url.tags:
            tags = url.tags.split(",")

        return Url(
            id=url.id,
            guid=url.guid,
            index=url.index,
            title=url.title,
            date_added=url.date_added,
            date_modified=url.date_modified,
            url=url.url,
            icon=url.icon,
            icon_uri=url.icon_uri,
            tags=tags,
        )

    def as_html(self, tree: Bookmark) -> str:
        """Converts bookmark object tree to HTML."""
        footer = "</DL>\n"

        self._stack = tree.children[::-1]
        body = []

        while self._stack:
            stack_item = self._stack.pop()
            folder = self._iterate_folder_html(stack_item)
            if not folder:
                continue

            self._create_placeholder(body, folder, stack_item)

        self._stack = None
        return indent_html("".join([BOOKMARKIE_HTML_HEADER, *body, footer]))

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
            folder_html += f' {BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_HTML_FLAG}="true"'
            title = BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE
        elif folder.special_folder == SpecialFolder.OTHER:
            folder_html += f' {BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_HTML_FLAG}="true"'
            title = BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE
        elif folder.special_folder == SpecialFolder.MOBILE:
            folder_html += f' {BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_HTML_FLAG}="true"'
            title = BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE

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

        We need to extract the folders 'Bookmarks Toolbar',  'Other Bookmarks', and 'Mobile Bookmarks',
        then insert them into the root folder.s children.

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
                "title": BOOKMARKIE_BOOKMARKS_ROOT_FOLDER_TITLE,
                "date_added": round(time.time() * 1000),
            },
        )
        new_tree.children.append(tree)
        children = []
        while tree.children:
            child = tree.children.pop(0)
            if (
                BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_HTML_FLAG.lower() in child.attrs
                or BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_HTML_FLAG.lower() in child.attrs
                or BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_HTML_FLAG.lower() in child.attrs
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
        if node.title == BOOKMARKIE_BOOKMARKS_MENU_FOLDER_TITLE:
            return SpecialFolder.MENU

        elif (
            BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_HTML_FLAG.lower() in node.attrs
            or node.title == BOOKMARKIE_BOOKMARKS_TOOLBAR_FOLDER_TITLE
        ):
            return SpecialFolder.TOOLBAR

        elif (
            BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_HTML_FLAG.lower() in node.attrs
            or node.title == BOOKMARKIE_BOOKMARKS_OTHER_FOLDER_TITLE
        ):
            return SpecialFolder.OTHER

        elif (
            BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_HTML_FLAG.lower() in node.attrs
            or node.title == BOOKMARKIE_BOOKMARKS_MOBILE_FOLDER_TITLE
        ):
            return SpecialFolder.MOBILE

    def as_json(self, tree: Bookmark) -> dict:
        """Convert the imported bookmarks to JSON."""
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

    def _folder_as_json(self, folder: Folder) -> dict:
        folder_json = {
            "id": folder.id,
            "guid": self._ensure_guid(folder.guid),
            "index": folder.index,
            "title": folder.title,
            "date_added": folder.date_added,
            "date_modified": folder.date_modified,
            "type": "folder",
        }

        if isinstance(folder.special_folder, SpecialFolder):
            folder_json["special_folder"] = folder.special_folder.value
            folder_json["title"] = BOOKMARKIE_SPECIAL_FOLDER_TO_TITLE[folder.special_folder]

        # we add the children at the end to make the json dump to the file more readable.
        folder_json["children"] = []

        return folder_json

    def _url_as_json(self, url: Url) -> dict:
        return {
            "id": url.id,
            "guid": self._ensure_guid(url.guid),
            "index": url.index,
            "title": url.title,
            "date_added": url.date_added,
            "date_modified": url.date_modified,
            "url": url.url,
            "icon": url.icon,
            "iconuri": url.icon_uri,
            "tags": url.tags,
            "type": "url",
        }

    @staticmethod
    def _ensure_guid(guid: str) -> str:
        """Ensure that we have a proper guid of type uuid4"""
        try:
            UUID(guid, version=4)
        except ValueError:
            guid = str(uuid4())
        return guid

    def from_json(self, filepath: Path) -> Bookmark:
        """Imports the JSON Bookmarks file as a Bookmark tree."""
        with filepath.open("r", encoding="utf-8") as file:
            # use the object_hook to load the json tree as a Bookmark tree.
            tree = json.load(file, object_hook=self._json_to_object)
        return tree

    @staticmethod
    def _json_to_object(jdict: dict) -> Bookmark:
        """Helper function used as object_hook for json load."""

        kwargs = {
            "id": int(jdict.pop("id")),
            "index": int(jdict.pop("index")),
            "title": jdict.pop("title", None),
            "date_added": int(jdict.pop("date_added", 0)),
            "date_modified": int(jdict.pop("date_modified", 0)),
            "guid": jdict.pop("guid", str(uuid4())),
        }

        type_ = jdict.pop("type")
        if type_ == TYPE_FOLDER:
            kwargs["children"] = jdict.pop("children", [])
            special_folder = jdict.pop("special_folder", "")
            if special_folder:
                special_folder = FolderRoot[special_folder].value
                kwargs["special_folder"] = special_folder
                kwargs["title"] = BOOKMARKIE_SPECIAL_FOLDER_TO_TITLE[special_folder]
            return Folder(**kwargs)
        elif type_ == TYPE_URL:
            kwargs["url"] = jdict.pop("url")
            kwargs["icon"] = jdict.pop("icon", "")
            kwargs["icon_uri"] = jdict.pop("iconuri", "")
            kwargs["tags"] = jdict.pop("tags", [])
            return Url(**kwargs)
        else:
            raise NotImplementedError(f"Unsupported type {type_}")
