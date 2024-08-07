import itertools
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import uuid4

from bs4 import Tag
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import backref, declarative_base, relationship, sessionmaker

TYPE_FOLDER = "folder"
TYPE_URL = "url"

engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class SpecialFolder(Enum):
    ROOT = "root"
    MENU = "menu"
    TOOLBAR = "toolbar"
    OTHER = "other"
    MOBILE = "mobile"


@dataclass
class Bookmark:
    id: int
    guid: str
    index: int
    title: str
    date_added: int
    date_modified: int


@dataclass
class Folder(Bookmark):
    special_folder: Optional[SpecialFolder] = ""
    children: list[Bookmark] = field(default_factory=list)


@dataclass
class Url(Bookmark):
    url: str
    icon: str = ""
    icon_uri: str = ""
    tags: list[str] = field(default_factory=list)

    def icon_uri_is_set(self) -> bool:
        return self.icon_uri != ""


class DBBookmark(Base):
    """Base model for the Url and Folder model.
    (used for Single Table Inheritance)
    ...
    Attributes
    ----------
    id : int
        id of the bookmark (url/folder)
    title : str
        title of bookmark (url/folder)
    date_added : datetime
        date bookmark (url/folder) was added on
    index : int
        current index to remember order of bookmark (url/folder) in folder
    parent_id : int
        id of the folder the bookmark (url/folder) is contained in
    parent : relation
        Many to One relation for the Folder, containing the
        bookmarks (url/folder)
    """

    __tablename__ = "bookmark"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    index = Column(Integer)
    parent_id = Column(Integer, ForeignKey("bookmark.id"), nullable=True)
    date_added = Column(Integer, nullable=False, default=round(time.time() * 1000))
    type = Column(String)
    parent = relationship(
        "DBBookmark",
        cascade="save-update, merge",
        backref=backref("children", cascade="all", order_by="DBBookmark.index"),
        lazy=False,
        remote_side="DBBookmark.id",
    )

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "bookmark"}

    def insert(self):
        """Insert a Bookmark object into the database."""
        session.add(self)
        session.commit()

    def update(self):
        """Update a Bookmark object in the database"""
        session.commit()

    def delete(self):
        """Delete a Bookmark object from the database"""
        session.delete(self)
        session.commit()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        # skip if the attribute is '_sa_instance_state' which is in
        # .__dict__ and vars(), since the object is a sqlalchemy object.
        remove = "_sa_instance_state"
        vars_self = vars(self).copy()
        vars_other = vars(other).copy()
        del vars_self[remove]
        del vars_other[remove]
        return vars_self == vars_other


class DBFolder(DBBookmark):
    """Model representing bookmark folders
    ...
    Attributes
    ----------
    id : int
        id of the folder
    title : str
        name of the folder
    date_added : datetime
        date folder was added on
    parent_id : int
        id of parent folder
    index : int
        current index in parent folder
    children : db relationship
        urls contained in the folder"""

    __mapper_args__ = {"polymorphic_identity": "folder"}

    def __init__(self, title, index, parent_id, _id=None, date_added=None):
        if _id:
            self.id = _id
        self.title = title
        self.index = index
        self.parent_id = parent_id
        self.date_added = date_added


class DBUrl(DBBookmark):
    """Model representing the URLs
    ...
    Attributes
    ----------
    id : int
        id of the url
    title : str
        title of url
    url : str
        url address
    date_added : datetime
        date url was added on
    icon : str
        html icon data
    icon_uri : str
        html icon_uri found in firefox bookmarks
    tags : str
        tags describing url
    index : int
        current index to remember order of urls in folder
    parent_id : int
        id of the folder the url is contained in"""

    url = Column(String)
    icon = Column(String)
    icon_uri = Column(String)
    tags = Column(String)

    __mapper_args__ = {"polymorphic_identity": "url"}

    def __init__(
        self,
        title,
        index,
        parent_id,
        url,
        _id=None,
        date_added=None,
        icon=None,
        icon_uri=None,
        tags=None,
    ):
        if _id:
            self.id = _id
        if title == None:
            self.title = url
        else:
            self.title = title
        self.index = index
        self.parent_id = parent_id
        self.date_added = date_added
        self.url = url
        self.icon = icon
        self.icon_uri = icon_uri
        self.tags = tags


class HTMLBookmark(Tag):
    """TreeBuilder class, used to add additional functionality to the
    BeautifulSoup Tag class. The following functionality is added:

    - add id to each folder("h3")/url("a") being imported, the id count starts at `2`.
        this is because the id `1` is reserved for the root folder which is not parsed by
        the BeautifulSoup Tag class.
    - add property access to the Tag class' attributes
      (date_added, date_modified, icon, icon_uri, id, index, title, type and url)
      which are usually found in the 'self.attrs' dictionary.
    - add a setter for (id and title)
    - change the self.children from an iterator `iter(self.contents)`
    to a list `self.contents` directly"""

    # Counter used to add the `id` to each element parsed.
    id_counter = itertools.count(start=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.name in ("a", "h3"):
            if not self.attrs.get("id"):
                self.attrs["id"] = next(__class__.id_counter)
        self.attrs["guid"] = str(uuid4())

    @property
    def date_added(self) -> int:
        """The date_added value in html bookmarks is in seconds, so we convert to microseconds"""
        date_added = self.attrs.get("add_date")
        if not date_added:
            date_added = round(time.time() * 1000)
        return int(date_added) * 1000_000

    @property
    def date_modified(self) -> int:
        """The date_modified value in html bookmarks is in seconds, so we convert to microseconds"""
        date_modified = self.attrs.get("last_modified")
        if not date_modified:
            date_modified = 0
        return int(date_modified) * 1000_000

    @property
    def icon(self) -> str:
        return self.attrs.get("icon", "")

    @property
    def icon_uri(self) -> str:
        return self.attrs.get("icon_uri", "")

    @property
    def id(self):
        return self.attrs.get("id")

    @id.setter
    def id(self, new_id: int):
        self.attrs["id"] = new_id

    @property
    def guid(self) -> str:
        return self.attrs.get("guid")

    @property
    def index(self) -> int:
        return self.attrs.get("index")

    @property
    def title(self) -> str:
        return self.attrs.get("title")

    @title.setter
    def title(self, new_title: str):
        self.attrs["title"] = new_title

    @property
    def type(self) -> str:
        if self.name == "h3":
            return TYPE_FOLDER
        elif self.name == "a":
            return TYPE_URL

    @property
    def tags(self) -> list[str]:
        return self.attrs.get("tags", [])

    @property
    def url(self) -> str:
        return self.attrs.get("href")

    @property
    def children(self):
        """To standardize the access of children amongst the different
        Bookmark classes."""
        return self.contents

    @classmethod
    def reset_id_counter(cls):
        cls.id_counter = itertools.count(start=2)

    def _as_folder(self, index: int) -> Folder:
        return Folder(
            id=self.id,
            guid=self.guid,
            index=index,
            title=self.title,
            date_added=self.date_added,
            date_modified=self.date_modified,
            children=[],
        )

    def _as_url(self, index: int) -> Url:
        return Url(
            id=self.id,
            guid=self.guid,
            index=index,
            title=self.title,
            date_added=self.date_added,
            date_modified=self.date_modified,
            url=self.url,
            icon=self.icon,
            icon_uri=self.icon_uri,
            tags=self.tags,
        )
