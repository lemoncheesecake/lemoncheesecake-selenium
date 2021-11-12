import pytest
from selenium.webdriver.common.by import By

from lemoncheesecake_selenium import Selector


@pytest.fixture()
def selector():
    return Selector(None)


def _test_selection(selection, expected_by, expected_value):
    assert selection.by == expected_by
    assert selection.value == expected_value


def test_constructor():
    selector = Selector(None)
    assert selector.driver is None
    assert selector.timeout is 10
    assert selector.screenshot_on_exception is False


@pytest.mark.parametrize(
    "name,expected", (
        ("by_id", By.ID),
        ("by_xpath", By.XPATH),
        ("by_link_text", By.LINK_TEXT),
        ("by_partial_link_text", By.PARTIAL_LINK_TEXT),
        ("by_name", By.NAME),
        ("by_tag_name", By.TAG_NAME),
        ("by_class_name", By.CLASS_NAME),
        ("by_css_selector", By.CSS_SELECTOR)
    )
)
def test_by(selector, name, expected):
    selection = getattr(selector, name)("dummy")
    assert selection.by == expected
    assert selection.value == "dummy"
    assert selection.selector is selector


def test_timeout():
    selector = Selector(None, timeout=42)
    assert selector.timeout == 42


def test_screenshot_on_exception():
    selector = Selector(None, screenshot_on_exception=True)
    assert selector.screenshot_on_exception is True


def test_change_selector_class_default_timeout():
    assert Selector(None).timeout == Selector.DEFAULT_TIMEOUT

    orig_timeout = Selector.DEFAULT_TIMEOUT
    try:
        Selector.DEFAULT_TIMEOUT = 42
        assert Selector(None).timeout == 42
    finally:
        Selector.DEFAULT_TIMEOUT = orig_timeout


def test_change_selector_class_default_screenshot_on_exception():
    assert Selector(None).screenshot_on_exception == Selector.DEFAULT_SCREENSHOT_ON_EXCEPTION

    orig_setting = Selector.DEFAULT_SCREENSHOT_ON_EXCEPTION
    try:
        Selector.DEFAULT_SCREENSHOT_ON_EXCEPTION = True
        assert Selector(None).screenshot_on_exception is True
    finally:
        Selector.DEFAULT_SCREENSHOT_ON_EXCEPTION = orig_setting
