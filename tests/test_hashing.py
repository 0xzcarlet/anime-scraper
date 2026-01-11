from scraper.utils import hash_values


def test_hash_values_order_independent():
    first = hash_values(["b", "a"])
    second = hash_values(["a", "b"])
    assert first == second


def test_hash_values_empty():
    assert hash_values([]) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
