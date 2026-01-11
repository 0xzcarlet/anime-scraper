from scraper.utils import slugify


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_empty():
    assert slugify("***") == "unknown"
