import pytest

from adjunct import pagination


def test_paginator():
    # Test beginning pages
    assert list(pagination.paginator(1, 10)) == [1, 2, 3, 4, None, 10]
    assert list(pagination.paginator(2, 10)) == [1, 2, 3, 4, 5, None, 10]

    # Test middle pages
    assert list(pagination.paginator(5, 10)) == [1, 2, 3, 4, 5, 6, 7, 8, None, 10]

    # Test end pages
    assert list(pagination.paginator(9, 10)) == [1, None, 6, 7, 8, 9, 10]
    assert list(pagination.paginator(10, 10)) == [1, None, 7, 8, 9, 10]

    # Test small number of pages
    assert list(pagination.paginator(1, 3)) == [1, 2, 3]
    assert list(pagination.paginator(2, 3)) == [1, 2, 3]
    assert list(pagination.paginator(3, 3)) == [1, 2, 3]


def test_paginator_bounds():
    with pytest.raises(pagination.InvalidPageError):
        list(pagination.paginator(0, 10))
    with pytest.raises(pagination.InvalidPageError):
        list(pagination.paginator(-1, 10))
    with pytest.raises(pagination.InvalidPageError):
        list(pagination.paginator(11, 10))
    with pytest.raises(pagination.InvalidPageError):
        list(pagination.paginator(100, 10))
    with pytest.raises(pagination.InvalidPageError):
        list(pagination.paginator(1, 0))
    with pytest.raises(pagination.InvalidPageError):
        list(pagination.paginator(1, -5))
