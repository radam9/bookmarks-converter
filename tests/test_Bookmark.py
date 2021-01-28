from bookmarks_converter.models import Bookmark


def test_equality(url_custom):
    instance_a = Bookmark()
    instance_b = Bookmark()
    for key, value in url_custom.items():
        setattr(instance_a, key, value)
        setattr(instance_b, key, value)
    assert instance_a == instance_b


def test_equality_false():
    instance_a = Bookmark()
    instance_b = 0
    assert (instance_a == instance_b) == False
