import pytest
from selenium.webdriver.common.by import By

from lemoncheesecake_selenium import Selector


def _test_selection(selection, expected_by, expected_value):
    assert selection.by == expected_by
    assert selection.value == expected_value


def test_constructor():
    driver = object()
    selector = Selector(driver)  # noqa
    assert selector.driver is driver


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
def test_by(name, expected):
    driver = object()
    selector = Selector(driver)  # noqa
    selection = getattr(selector, name)("dummy")
    assert selection.by == expected
    assert selection.value == "dummy"
    assert selection.driver is driver
