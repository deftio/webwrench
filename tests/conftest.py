"""Shared fixtures for webwrench tests."""

import pytest

from webwrench._context import Element, Page, reset_default_page, get_default_page


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset the default page and element counter before each test."""
    reset_default_page()
    yield
    reset_default_page()
