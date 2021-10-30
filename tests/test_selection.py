import pytest
from unittest.mock import MagicMock, patch
import callee

from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import lemoncheesecake.api as lcc
from lemoncheesecake.matching.matcher import Matcher, MatchResult
from lemoncheesecake_selenium import Selector, Selection


@pytest.fixture
def log_info_mock(mocker):
    return mocker.patch("lemoncheesecake_selenium.selection.lcc.log_info")


@pytest.fixture
def log_check_mock(mocker):
    return mocker.patch("lemoncheesecake.matching.operations.log_check")


@pytest.fixture
def select_mock(mocker):
    return mocker.patch("lemoncheesecake_selenium.selection.Select")


@pytest.mark.parametrize("method_name", ["get_element", "get_element_or_abort"])
def test_get_element(method_name):
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    ret = getattr(selection, method_name)()
    assert isinstance(ret, MagicMock)
    mock.find_element.assert_called_with(By.ID, "value")


def test_get_element_not_found():
    mock = MagicMock()
    mock.find_element.side_effect = NoSuchElementException("value")
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(NoSuchElementException):
        selection.get_element()


def test_get_element_or_abort_not_found(log_info_mock):
    mock = MagicMock()
    mock.find_element.side_effect = NoSuchElementException("value")
    selector = Selector(mock)
    selection = selector.by_id("value")
    with pytest.raises(lcc.AbortTest):
        selection.get_element_or_abort()


def test_get_elements():
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    ret = selection.get_elements()
    assert isinstance(ret, MagicMock)
    mock.find_elements.assert_called_with(By.ID, "value")


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
    with pytest.raises(lcc.AbortTest):
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
    with pytest.raises(lcc.AbortTest):
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
    with pytest.raises(lcc.AbortTest):
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
        with pytest.raises(lcc.AbortTest):
            getattr(selection, method_name)(*args)


def test_select_failure_select_raises():
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.selection.Select") as select_mock:
        select_mock.side_effect = WebDriverException("error")
        with pytest.raises(lcc.AbortTest):
            selection.select_by_index(1)


def test_select_failure_select_by_raises():
    mock = MagicMock()
    selector = Selector(mock)
    selection = selector.by_id("value")
    with patch("lemoncheesecake_selenium.selection.Select") as select_mock:
        select_mock.return_value.select_by_index.side_effect = WebDriverException("error")
        with pytest.raises(lcc.AbortTest):
            selection.select_by_index(1)


class MyMatcher(Matcher):
    def __init__(self, result=MatchResult.success()):
        super().__init__()
        self.actual = None
        self.result = result

    def build_description(self, transformation):
        return "to be here"

    def matches(self, actual):
        self.actual = actual
        return self.result


def test_check_element_success(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = "dummy"
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher()
    selection.check_element(matcher)
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", True, None)
    assert matcher.actual == "dummy"


def test_check_element_failure_match(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = "dummy"
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher(result=MatchResult.failure())
    selection.check_element(matcher)
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", False, None)
    assert matcher.actual == "dummy"


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
    mock.find_element.return_value = "dummy"
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher()
    selection.require_element(matcher)
    log_check_mock.assert_called_with("Expect element identified by id 'value' to be here", True, None)
    assert matcher.actual == "dummy"


def test_assert_element(log_check_mock):
    mock = MagicMock()
    mock.find_element.return_value = "dummy"
    selector = Selector(mock)
    selection = selector.by_id("value")
    matcher = MyMatcher()
    selection.assert_element(matcher)
    log_check_mock.assert_not_called()
    assert matcher.actual == "dummy"
