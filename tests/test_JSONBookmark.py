from bookmarks_converter.models import JSONBookmark


def test_JSONBookmark_url_chrome(url_chrome):
    url = JSONBookmark(**url_chrome)
    assert isinstance(url.date_added, int)
    # we automatically add 1 to id when importing from chrome.
    assert int(url_chrome.get("id")) == url.id - 1
    assert url_chrome.get("name") == url.title
    assert url_chrome.get("type") == url.type
    assert url_chrome.get("url") == url.url


def test_JSONBookmark_folder_chrome(folder_chrome):
    folder = JSONBookmark(**folder_chrome)
    assert isinstance(folder.children, list)
    assert isinstance(folder.date_added, int)
    # we automatically add 1 to id when importing from chrome.
    assert int(folder_chrome.get("id")) == folder.id - 1
    assert folder_chrome.get("name") == folder.title
    assert folder_chrome.get("type") == folder.type


def test_JSONBookmark_url_firefox(url_firefox):
    url = JSONBookmark(**url_firefox)
    assert url_firefox.get("title") == url.title
    assert url_firefox.get("index") == url.index
    assert url_firefox.get("dateAdded") == url.date_added
    assert url_firefox.get("id") == url.id
    assert url_firefox.get("iconuri") == url.icon_uri
    # firefox url type name is "text/x-moz-place"
    # make sure it was converted to url correctly
    assert "url" == url.type
    assert url_firefox.get("uri") == url.url


def test_JSONBookmark_folder_firefox(folder_firefox):
    folder = JSONBookmark(**folder_firefox)
    assert folder_firefox.get("title") == folder.title
    assert folder_firefox.get("index") == folder.index
    assert folder_firefox.get("dateAdded") == folder.date_added
    assert folder_firefox.get("id") == folder.id
    # firefox folder type name is "text/x-moz-place-container"
    # make sure it was converted to folder correctly
    assert "folder" == folder.type
    assert isinstance(folder.children, list)


def test_JSONBookmark_url_custom(url_custom):
    url = JSONBookmark(**url_custom)
    assert url_custom.get("type") == url.type
    assert url_custom.get("id") == url.id
    assert url_custom.get("index") == url.index
    assert url_custom.get("parent_id") == url.parent_id
    assert url_custom.get("title") == url.title
    assert url_custom.get("date_added") == url.date_added
    assert url_custom.get("icon") == url.icon
    assert url_custom.get("iconuri") == url.icon_uri
    assert url_custom.get("tags") == url.tags


def test_JSONBookmark_folder_custom(folder_custom):
    folder = JSONBookmark(**folder_custom)
    assert folder_custom.get("type") == folder.type
    assert folder_custom.get("id") == folder.id
    assert folder_custom.get("index") == folder.index
    assert folder_custom.get("parent_id") == folder.parent_id
    assert folder_custom.get("title") == folder.title
    assert folder_custom.get("date_added") == folder.date_added
    assert isinstance(folder_custom.get("children"), list)


def test_JSONBookmark_convert_url_to_json(url_custom):
    url = JSONBookmark(**url_custom)
    assert url._convert_url_to_json() == url_custom


def test_JSONBookmark_convert_folder_to_json(folder_custom):
    folder = JSONBookmark(**folder_custom)
    assert folder._convert_folder_to_json() == folder_custom
