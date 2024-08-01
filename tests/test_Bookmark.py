from bookmarks_converter.models import DBBookmark


def test_equality(url_custom):
    instance_a = DBBookmark()
    instance_b = DBBookmark()
    for key, value in url_custom.items():
        setattr(instance_a, key, value)
        setattr(instance_b, key, value)
    assert instance_a == instance_b


def test_equality_false():
    instance_a = DBBookmark()
    instance_b = 0
    assert (instance_a == instance_b) == False
