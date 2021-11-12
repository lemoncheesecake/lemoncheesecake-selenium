import pytest
from unittest.mock import MagicMock, patch
import callee

from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
import lemoncheesecake.api as lcc
from lemoncheesecake.matching.matcher import MatchResult
from lemoncheesecake_selenium import Selector

from helpers import MyMatcher


FAKE_WEB_ELEMENT = object()


@pytest.fixture
def log_info_mock(mocker):
    return mocker.patch("lemoncheesecake_selenium.selection.lcc.log_info")


@pytest.fixture
def log_check_mock(mocker):
    return mocker.patch("lemoncheesecake.matching.operations.log_check")


@pytest.fixture
def prepare_image_attachment_mock(mocker):
    return mocker.patch("lemoncheesecake_selenium.selection.lcc.prepare_image_attachment")


@pytest.fixture
def select_mock(mocker):
    return mocker.patch("lemoncheesecake_selenium.selection.Select")


def test_element():
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    ret = selection.element
    assert isinstance(ret, MagicMock)
    mock.find_element.assert_called_with(By.ID, "value")


def test_element_not_found():
    mock = MagicMock()
    mock.find_element.side_effect = NoSuchElementException("value")
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(NoSuchElementException):
        selection.element  # noqa


def test_elements():
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    ret = selection.elements
    assert isinstance(ret, MagicMock)
    mock.find_elements.assert_called_with(By.ID, "value")


@pytest.mark.parametrize(
    "method_name,expected",
    (
        ("by_id", "element identified by id 'value'"),
        ("by_xpath", "element identified by XPATH 'value'"),
        ("by_link_text", "element identified by link text 'value'"),
        ("by_partial_link_text", "element identified by partial link text 'value'"),
        ("by_name", "element identified by name 'value'"),
        ("by_tag_name", "element identified by tag name 'value'"),
        ("by_class_name", "element identified by class name 'value'"),
        ("by_css_selector", "element identified by CSS selector 'value'")
    )
)
def test_str(method_name, expected):
    selector = Selector(None)
    selection = getattr(selector, method_name)("value")
    assert str(selection) == expected


def test_click(log_info_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.click()
    assert mock.find_element.return_value.click.called
    log_info_mock.assert_called_with(callee.StartsWith("Click on"))


def test_click_failure(log_info_mock):
    mock = MagicMock()
    mock.find_element.return_value.click.side_effect = WebDriverException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(WebDriverException):
        selection.click()


def test_set_text(log_info_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.set_text("content")
    mock.find_element.return_value.send_keys.assert_called_with("content")
    log_info_mock.assert_called_with(callee.StartsWith("Set text"))


def test_set_text_failure(log_info_mock):
    mock = MagicMock()
    mock.find_element.return_value.send_keys.side_effect = WebDriverException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(WebDriverException):
        selection.set_text("content")


def test_clear(log_info_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.clear()
    mock.find_element.return_value.clear.assert_called()
    log_info_mock.assert_called_with(callee.StartsWith("Clear"))


def test_clear_failure(log_info_mock):
    mock = MagicMock()
    mock.find_element.return_value.clear.side_effect = WebDriverException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(WebDriverException):
        selection.clear()


def _test_select(log_info_mock, method_name, args, expected_log):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.selection.Select") as select_mock:
        getattr(selection, method_name)(*args)
    getattr(select_mock.return_value, method_name).assert_called_with(*args)
    log_info_mock.assert_called_with(expected_log)


@pytest.mark.parametrize(
    "method_name",
    ("select_by_value", "select_by_index", "select_by_visible_text")
)
def test_select(log_info_mock, method_name):
    _test_select(log_info_mock, method_name, ("arg",), callee.StartsWith("Select"))


@pytest.mark.parametrize(
    "method_name,args",
    (("deselect_all", ()),
     ("deselect_by_value", ("opt",)), ("deselect_by_index", (1,)), ("deselect_by_visible_text", ("opt",)))
)
def test_deselect(log_info_mock, method_name, args):
    _test_select(log_info_mock, method_name, args, callee.StartsWith("Deselect"))


def _test_select_failure(method_name, args):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.selection.Select") as select_mock:
        select_mock.side_effect = WebDriverException("error")
        with pytest.raises(WebDriverException):
            getattr(selection, method_name)(*args)


def test_select_failure_select_raises(log_info_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.selection.Select") as select_mock:
        select_mock.side_effect = WebDriverException("error")
        with pytest.raises(WebDriverException):
            selection.select_by_index(1)


def test_select_failure_select_by_raises(log_info_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.selection.Select") as select_mock:
        select_mock.return_value.select_by_index.side_effect = WebDriverException("error")
        with pytest.raises(WebDriverException):
            selection.select_by_index(1)


def test_check_element_success(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher()
    selection.check_element(matcher)
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", True, None)
    assert matcher.actual is FAKE_WEB_ELEMENT


def test_check_element_failure_match(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher(result=MatchResult.failure())
    selection.check_element(matcher)
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", False, None)
    assert matcher.actual is FAKE_WEB_ELEMENT


def test_check_element_failure_not_found(log_check_mock):
    mock = MagicMock()
    mock.find_element.side_effect = NoSuchElementException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher(result=MatchResult.failure())
    selection.check_element(matcher)
    log_check_mock.assert_called_with(
        "Expect element identified by id 'value' to be here", False, callee.StartsWith("Could not find")
    )


# only perform basic tests on require_element & assert_element methods since they
# are simple calls to their lemoncheesecake counterparts
# the matcher wrapping system is already tested in depth the `test_check_element_*` tests

def test_require_element(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher()
    selection.require_element(matcher)
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", True, None)
    assert matcher.actual is FAKE_WEB_ELEMENT


def test_assert_element(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher()
    selection.assert_element(matcher)
    log_check_mock.assert_not_called()
    assert matcher.actual is FAKE_WEB_ELEMENT


def test_with_must_be_waited_until():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.must_be_waited_until(lambda _: lambda _: True, timeout=0)
    assert selection.element is FAKE_WEB_ELEMENT


def test_with_must_be_waited_until_extra_args():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.must_be_waited_until(lambda arg1, arg2: lambda arg: True, timeout=0, extra_args=("value",))
    assert selection.element is FAKE_WEB_ELEMENT


def test_with_must_be_waited_until_failure():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.must_be_waited_until(lambda _: lambda _: False, timeout=0)
    with pytest.raises(TimeoutException):
        assert selection.element


def test_with_must_be_waited_until_not_success():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock, timeout=0)
    selection = selector.by_id("value")
    selection.must_be_waited_until_not(lambda _: lambda _: False)
    assert selection.element is FAKE_WEB_ELEMENT


def test_with_must_be_waited_until_not_extra_args():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock, timeout=0)
    selection = selector.by_id("value")
    selection.must_be_waited_until_not(lambda arg1, arg2: lambda arg: False, extra_args=("value",))
    assert selection.element is FAKE_WEB_ELEMENT


def test_with_must_be_waited_until_not_failure():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock, timeout=0)
    selection = selector.by_id("value")
    selection.must_be_waited_until_not(lambda _: lambda _: True)
    with pytest.raises(TimeoutException):
        assert selection.element


@pytest.mark.parametrize(
    "action", (
        lambda s: s.click(),
        lambda s: s.clear(),
        lambda s: s.set_text("foo"),
        lambda s: s.select_by_value("foo"),
        lambda s: s.select_by_index(1),
        lambda s: s.select_by_visible_text("foo"),
        lambda s: s.deselect_all(),
        lambda s: s.deselect_by_index(1),
        lambda s: s.deselect_by_value("foo"),
        lambda s: s.deselect_by_visible_text("foo")
    )
)
def test_screenshot_on_exception(log_info_mock, action):
    driver_mock = MagicMock()
    driver_mock.find_element.side_effect = WebDriverException()
    selector = Selector(driver_mock, screenshot_on_exception=True)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.utils.lcc.prepare_image_attachment") as mock:
        with pytest.raises(WebDriverException):
            action(selection)
        mock.assert_called()


def test_save_screenshot(prepare_image_attachment_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.save_screenshot()
    prepare_image_attachment_mock.assert_called_with(
        "screenshot.png", "Screenshot of element identified by id 'value'"
    )
    mock.find_element.return_value.screenshot.assert_called_with(callee.Any())


def test_save_screenshot_with_description(prepare_image_attachment_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.save_screenshot("some description")
    prepare_image_attachment_mock.assert_called_with(
        "screenshot.png", "some description"
    )
    mock.find_element.return_value.screenshot.assert_called_with(callee.Any())


def test_save_screenshot_exception_raised_by_find_element(prepare_image_attachment_mock):
    mock = MagicMock()
    mock.find_element.side_effect = NoSuchElementException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(NoSuchElementException):
        selection.save_screenshot()


def test_save_screenshot_exception_raised_by_screenshot(prepare_image_attachment_mock):
    mock = MagicMock()
    mock.find_element.return_value.screenshot.side_effect = WebDriverException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(WebDriverException):
        selection.save_screenshot()
