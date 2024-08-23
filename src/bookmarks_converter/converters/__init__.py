from bookmarks_converter.converters.bookmarkie import Bookmarkie
from bookmarks_converter.converters.chrome import Chrome
from bookmarks_converter.converters.firefox import Firefox

_CONVERTERS = (Bookmarkie, Chrome, Firefox)
CONVERTERS = {c.__name__.lower(): c for c in _CONVERTERS}
CONVERTER_NAMES = tuple(sorted(c.__name__.lower() for c in _CONVERTERS))
CONVERTER_FORMATS = tuple(sorted({f for c in _CONVERTERS for f in c.formats}))
