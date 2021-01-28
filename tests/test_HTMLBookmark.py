from bookmarks_converter.models import HTMLBookmark


def test_HTMLBookmark_url_custom(url_custom):
    url = HTMLBookmark(name="a", attrs=url_custom)
    assert isinstance(url_custom.get("date_added"), int)
    assert url_custom.get("icon") == url.icon
    assert url_custom.get("iconuri") == url.icon_uri
    assert url_custom.get("id") == url.id
    assert url_custom.get("index") == url.index
    assert url_custom.get("title") == url.title
    assert url_custom.get("type") == url.type
    assert "url" == url.type
    assert url_custom.get("href") == url.url
    # test @property.setter for id/index/title
    url.id = url.index = 9000
    url.title = "Over 9000"
    assert 9000 == url.id
    assert 9000 == url.index
    assert "Over 9000" == url.title


def test_HTMLBookmark_folder_custom(folder_custom):
    folder = HTMLBookmark(name="h3", attrs=folder_custom)
    assert isinstance(folder_custom.get("date_added"), int)
    assert folder_custom.get("id") == folder.id
    assert folder_custom.get("index") == folder.index
    assert folder_custom.get("title") == folder.title
    assert folder_custom.get("type") == folder.type
    assert "folder" == folder.type
    assert isinstance(folder.contents, list)
    assert isinstance(folder.children, list)
