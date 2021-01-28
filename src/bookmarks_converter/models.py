import itertools
import time

from bs4 import Tag
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class NodeMixin:
    """Mixin class containing the methods used to create folders/urls in
    different formats HTML/JSON/DB, used in the creation of new bookmark tree
    in a different format."""

    def _convert_folder_to_db(self):
        """Convert a (html or json) folder object to a database folder object."""
        self._check_instance_type("folder")
        folder = Folder(
            _id=self.id,
            index=self.index,
            parent_id=self.parent_id,
            title=self.title,
            date_added=self.date_added,
        )
        return folder

    def _convert_url_to_db(self):
        """Convert a url (html or json) object to a database url object."""
        self._check_instance_type("url")
        url = Url(
            _id=self.id,
            index=self.index,
            parent_id=self.parent_id,
            title=self.title,
            date_added=self.date_added,
            url=self.url,
            icon=self.icon,
            icon_uri=self.icon_uri,
            tags=self.tags,
        )
        return url

    def _convert_folder_to_html(self):
        """Convert a (database or json) folder object to a html folder string."""
        self._check_instance_type("folder")
        if self.title in ("Bookmarks Toolbar", "Bookmarks bar", "toolbar"):
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0" PERSONAL_TOOLBAR_FOLDER="true">{self.title}</H3>\n'
        elif self.title in ("Other Bookmarks", "unfiled"):
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0" UNFILED_BOOKMARKS_FOLDER="true">{self.title}</H3>\n'
        else:
            return f'<DT><H3 ADD_DATE="{self.date_added}" LAST_MODIFIED="0">{self.title}</H3>\n'

    def _convert_url_to_html(self):
        """Convert a (database or json) url object to a html url string."""
        self._check_instance_type("url")
        return f'<DT><A HREF="{self.url}" ADD_DATE="{self.date_added}" LAST_MODIFIED="0" ICON_URI="{self.icon_uri}" ICON="{self.icon}">{self.title}</A>\n'

    def _convert_folder_to_json(self):
        """Convert a (database or html) folder object to a json folder object."""
        self._check_instance_type("folder")
        folder = {
            "type": self.type,
            "id": self.id,
            "index": self.index,
            "title": self.title,
            "date_added": self.date_added,
            "children": [],
        }
        return folder

    def _convert_url_to_json(self):
        """Convert a (database or html) url object to a json url object."""
        self._check_instance_type("url")
        url = {
            "type": self.type,
            "id": self.id,
            "index": self.index,
            "title": self.title,
            "date_added": self.date_added,
            "url": self.url,
            "icon": self.icon,
            "iconuri": self.icon_uri,
            "tags": self.tags,
        }
        return url

    def _check_instance_type(self, type_):
        """"Check that the type of the instance matches the type of executed method"""
        if self.type != type_:
            raise TypeError(f"The item you are converting is not a {type_}")

    def __iter__(self):
        """Iterating over an Object iterates over its contents."""
        return iter(self.children)

    def __repr__(self):
        """Bookmark object representation"""
        return f"{self.title} - {self.type} - id: {self.id}"


class Bookmark(Base, NodeMixin):
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
        "Bookmark",
        cascade="save-update, merge",
        backref=backref("children", cascade="all", order_by="Bookmark.index"),
        lazy=False,
        remote_side="Bookmark.id",
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


class Folder(Bookmark):
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


class Url(Bookmark):
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


class JSONBookmark(NodeMixin):
    """JSON Bookmark class used to create objects out of the folders/urls in a
    json bookmarks file while importing (json.load) using the object_hook.

    Attributes:
    ----------
    id: int
        id of the element
    index : int
        index (position) of the element in its parent
    parent_id : int
        id of the element's parent
    title : str
        title (name) of the element
    date_added : float
        date (time since epoch) at which the element was
    created/added to the bookmarks
    type : str
        element type (folder or url)
    children : list of dict
        children of the current element
    source : str
        source of bookmark element (chrome/firefox/bookmarkie)

    Parameters:
    -----------
    The class expects a mix of parameters similar to the attributes, they vary
    depending on the element type (folder/url)"""

    def __init__(self, **kwargs):

        # check the version of the passed json file depending on unique elements
        # that exist in each source.
        if "name" in kwargs:
            self.source = "Chrome"
        elif "typeCode" in kwargs:
            self.source = "Firefox"
        else:
            self.source = "Bookmarkie"

        self.id = int(kwargs.pop("id"))
        self.index = kwargs.pop("index", None)
        self.parent_id = kwargs.pop("parent_id", None)
        # chrome uses different key for title
        self.title = kwargs.pop("title", kwargs.pop("name", None))
        # firefox uses different key for date_added
        self.date_added = int(kwargs.pop("date_added", kwargs.pop("dateAdded", None)))

        temp = kwargs.pop("type")
        if temp in ("folder", "text/x-moz-place-container"):
            self.type = "folder"
            self.children = kwargs.pop("children", [])
        elif temp in ("url", "text/x-moz-place"):
            self.type = "url"
            # firefox uses different key for url
            self.url = kwargs.pop("url", kwargs.pop("uri", None))
            self.icon = kwargs.pop("icon", None)
            # firefox uses different key for icon_uri
            self.icon_uri = kwargs.pop("icon_uri", kwargs.pop("iconuri", None))
            self.tags = kwargs.pop("tags", None)

        if self.source == "Chrome":
            # chrome starts id from 0 not 1, add 1 to adjust
            self.id += 1
            # adjusting epoch for chrome timestamp
            self.date_added = self.date_added - 11644473600000000


class HTMLBookmark(Tag, NodeMixin):
    """TreeBuilder class, used to add additional functionality to the
    BeautifulSoup Tag class. The following functionality is added:

    - add id to each folder("h3")/url("a") being imported
    - add property access to the Tag class' attributes
      (date_added, icon, icon_uri, id, index, title, type and url)
      which are usually found at the 'self.attrs' dictionary.
    - add a setter for (id, index and title)
    - redirect the self.children from an iterator `iter(self.contents)`
    to a list `self.contents` directly"""

    id_counter = itertools.count(start=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.name in ("a", "h3"):
            if not self.attrs.get("id"):
                self.attrs["id"] = next(__class__.id_counter)

    @property
    def date_added(self):
        """Redirect the `add_date` lookup to a `date_added` attribute.
        add a `date_added` with current datetime if it doesn't exist"""
        date_added = self.attrs.get("add_date")
        if not date_added:
            date_added = round(time.time() * 1000)
        return int(date_added)

    @property
    def icon(self):
        """Redirect the `icon` lookup to a `icon` attribute."""
        return self.attrs.get("icon")

    @property
    def icon_uri(self):
        """Redirect the `iconuri` lookup to a `icon_uri` attribute."""
        return self.attrs.get("iconuri")

    @property
    def id(self):
        """Redirect the `id` lookup to a `id` attribute."""
        return self.attrs.get("id")

    @id.setter
    def id(self, new_id):
        self.attrs["id"] = new_id

    @property
    def index(self):
        """Redirect the `index` lookup to a `index` attribute."""
        return self.attrs.get("index")

    @index.setter
    def index(self, new_index):
        self.attrs["index"] = new_index

    @property
    def title(self):
        """Redirect the `title` lookup to a `title` attribute."""
        return self.attrs.get("title")

    @title.setter
    def title(self, new_title):
        self.attrs["title"] = new_title

    @property
    def type(self):
        """Add a type attribute defining the type of object the instance is."""
        if self.name == "h3":
            return "folder"
        elif self.name == "a":
            return "url"

    @property
    def url(self):
        """Redirect the `href` lookup to a `url` attribute."""
        return self.attrs.get("href")

    @property
    def children(self):
        """To standardize the access of children amongst the different
        Bookmark classes."""
        return self.contents

    @classmethod
    def reset_id_counter(cls):
        """Reset the id_counter."""
        cls.id_counter = itertools.count(start=2)
