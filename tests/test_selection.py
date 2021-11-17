import pytest
from unittest.mock import MagicMock, patch
from callee import StartsWith, Any, Contains

from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
import lemoncheesecake.api as lcc
from lemoncheesecake.matching.matcher import MatchResult
from lemoncheesecake_selenium import Selector, Selection

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
    return mocker.patch("lemoncheesecake.api.prepare_image_attachment")


@pytest.fixture
def select_mock(mocker):
    return mocker.patch("lemoncheesecake_selenium.selection.Select")


@pytest.fixture
def preserve_selection_settings():
    orig_default_timeout = Selection.default_timeout
    orig_screenshot_on_exceptions = Selection.screenshot_on_exceptions
    orig_screenshot_on_failed_checks = Selection.screenshot_on_failed_checks
    yield
    Selection.default_timeout = orig_default_timeout
    Selection.screenshot_on_exceptions = orig_screenshot_on_exceptions
    Selection.screenshot_on_failed_checks = orig_screenshot_on_failed_checks


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
    selector = Selector(None)  # noqa
    selection = getattr(selector, method_name)("value")
    assert str(selection) == expected


def test_click(log_info_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.click()
    assert mock.find_element.return_value.click.called
    log_info_mock.assert_called_with(StartsWith("Click on"))


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
    log_info_mock.assert_called_with(StartsWith("Set text"))


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
    log_info_mock.assert_called_with(StartsWith("Clear"))


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
    _test_select(log_info_mock, method_name, ("arg",), StartsWith("Select"))


@pytest.mark.parametrize(
    "method_name,args",
    (("deselect_all", ()),
     ("deselect_by_value", ("opt",)), ("deselect_by_index", (1,)), ("deselect_by_visible_text", ("opt",)))
)
def test_deselect(log_info_mock, method_name, args):
    _test_select(log_info_mock, method_name, args, StartsWith("Deselect"))


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
        "Expect element identified by id 'value' to be here", False, StartsWith("Could not find")
    )


@pytest.mark.parametrize(
    "method_name", ("check_element", "require_element", "assert_element")
)
@pytest.mark.usefixtures("preserve_selection_settings")
def test_check_element_failure_match_with_screenshot(log_check_mock, prepare_image_attachment_mock, method_name):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher(result=MatchResult.failure("Not found"))
    Selection.screenshot_on_failed_checks = True
    try:
        getattr(selection, method_name)(matcher)
    except lcc.AbortTest:  # require_element and assert_element will raise AbortTest
        pass
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", False, Any())
    prepare_image_attachment_mock.assert_called()
    assert matcher.actual is FAKE_WEB_ELEMENT


@pytest.mark.parametrize(
    "method_name,mock_raise_exception,abort_test_must_be_raised,check_outcome", (
        ("check_no_element", True, False, True),
        ("check_no_element", False, False, False),
        ("require_no_element", True, False, True),
        ("require_no_element", False, True, False),
        ("assert_no_element", True, False, None),
        ("assert_no_element", False, True, False)
    )
)
def test_check_no_element(log_check_mock,
                          method_name, mock_raise_exception, abort_test_must_be_raised, check_outcome):
    mock = MagicMock()
    if mock_raise_exception:
        mock.find_element.side_effect = NoSuchElementException()
    else:
        mock.find_element.return_value = FAKE_WEB_ELEMENT

    selector = Selector(mock)
    selection = selector.by_id("value")

    if abort_test_must_be_raised:
        with pytest.raises(lcc.AbortTest):
            getattr(selection, method_name)()
    else:
        getattr(selection, method_name)()

    if check_outcome is not None:
        log_check_mock.assert_called_with(
            "Expect element identified by id 'value' to not be present in page", check_outcome, Any()
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


def test_check_element_without_argument_success(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.check_element()
    log_check_mock.assert_called_with(Contains("present in page"), True, Any())


def test_check_element_without_argument_failure(log_check_mock):
    mock = MagicMock()
    mock.find_element.side_effect = NoSuchElementException()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.check_element()
    log_check_mock.assert_called_with(Contains("present in page"), False, Any())


def test_require_element_without_argument(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.require_element()
    log_check_mock.assert_called_with(Contains("present in page"), True, Any())


def test_assert_element_without_argument(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.assert_element()
    log_check_mock.assert_not_called()


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


@pytest.mark.usefixtures("preserve_selection_settings")
def test_with_must_be_waited_until_not_success():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    Selection.default_timeout = 0
    selection.must_be_waited_until_not(lambda _: lambda _: False)
    assert selection.element is FAKE_WEB_ELEMENT


@pytest.mark.usefixtures("preserve_selection_settings")
def test_with_must_be_waited_until_not_extra_args():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    Selection.default_timeout = 0
    selection.must_be_waited_until_not(lambda arg1, arg2: lambda arg: False, extra_args=("value",))
    assert selection.element is FAKE_WEB_ELEMENT


@pytest.mark.usefixtures("preserve_selection_settings")
def test_with_must_be_waited_until_not_failure():
    mock = MagicMock()
    mock.find_element.return_value = FAKE_WEB_ELEMENT
    selector = Selector(mock)
    selection = selector.by_id("value")
    Selection.default_timeout = 0
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
@pytest.mark.usefixtures("preserve_selection_settings")
def test_screenshot_on_exception(log_info_mock, prepare_image_attachment_mock, action):
    driver_mock = MagicMock()
    driver_mock.find_element.side_effect = WebDriverException()
    selector = Selector(driver_mock)
    selection = selector.by_id("value")
    Selection.screenshot_on_exceptions = True
    with pytest.raises(WebDriverException):
        action(selection)
    prepare_image_attachment_mock.assert_called()


def test_save_screenshot(prepare_image_attachment_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.save_screenshot()
    prepare_image_attachment_mock.assert_called_with(
        "screenshot.png", "Screenshot of element identified by id 'value'"
    )
    mock.find_element.return_value.screenshot.assert_called_with(Any())


def test_save_screenshot_with_description(prepare_image_attachment_mock):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    selection.save_screenshot("some description")
    prepare_image_attachment_mock.assert_called_with(
        "screenshot.png", "some description"
    )
    mock.find_element.return_value.screenshot.assert_called_with(Any())


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
