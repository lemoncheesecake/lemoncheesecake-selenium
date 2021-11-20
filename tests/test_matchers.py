from unittest.mock import MagicMock

import pytest
from callee import Regex
from lemoncheesecake.matching.matcher import MatchResult, MatcherDescriptionTransformer
from lemoncheesecake_selenium import has_text, has_attribute, has_property, \
    is_displayed, is_enabled, is_selected, is_in_page

from helpers import MyMatcher


MARKER = object()


def test_has_text_description():
    sub_matcher = MyMatcher()
    matcher = has_text(sub_matcher)
    assert matcher.build_description(MatcherDescriptionTransformer()) == "to have text that is here"


def test_has_text_success():
    mock = MagicMock()
    mock.text = "foo"
    sub_matcher = MyMatcher()
    matcher = has_text(sub_matcher)
    assert matcher.matches(mock)
    assert sub_matcher.actual == "foo"


def test_has_text_failure():
    mock = MagicMock()
    mock.text = "foo"
    sub_matcher = MyMatcher(MatchResult.failure())
    matcher = has_text(sub_matcher)
    assert not matcher.matches(mock)
    assert sub_matcher.actual == "foo"


@pytest.mark.parametrize("matcher_func", (has_attribute, has_property))
def test_has_attribute_description(matcher_func):
    matcher = matcher_func("foo")
    assert matcher.build_description(MatcherDescriptionTransformer()) == Regex(r"to have .+ 'foo'")


@pytest.mark.parametrize("matcher_func", (has_attribute, has_property))
def test_has_attribute_description_with_matcher(matcher_func):
    matcher = matcher_func("foo", MyMatcher())
    assert matcher.build_description(MatcherDescriptionTransformer()) == Regex(r"to have .+ 'foo' that is here")


@pytest.mark.parametrize(
    "matcher_func,mocked_func", (
        (has_attribute, "get_attribute"),
        (has_property, "get_property")
    )
)
def test_has_attribute_success(matcher_func, mocked_func):
    mock = MagicMock()
    matcher = matcher_func("foo")
    assert matcher.matches(mock)
    getattr(mock, mocked_func).assert_called_with("foo")


@pytest.mark.parametrize(
    "matcher_func,mocked_func", (
        (has_attribute, "get_attribute"),
        (has_property, "get_property")
    )
)
def test_has_attribute_success_with_matcher(matcher_func, mocked_func):
    mock = MagicMock()
    sub_matcher = MyMatcher()
    matcher = matcher_func("foo", sub_matcher)
    assert matcher.matches(mock) is sub_matcher.result
    getattr(mock, mocked_func).assert_called_with("foo")
    assert sub_matcher.actual is getattr(mock, mocked_func).return_value


@pytest.mark.parametrize(
    "matcher_func,mocked_func", (
        (has_attribute, "get_attribute"),
        (has_property, "get_property")
    )
)
def test_has_attribute_failure(matcher_func, mocked_func):
    mock = MagicMock()
    getattr(mock, mocked_func).return_value = None
    matcher = matcher_func("foo")
    assert not matcher.matches(mock)


@pytest.mark.parametrize("matcher_func", (has_attribute, has_property))
def test_has_attribute_failure_with_matcher(matcher_func):
    mock = MagicMock()
    sub_matcher = MyMatcher(result=MatchResult.failure())
    matcher = matcher_func("foo", sub_matcher)
    result = matcher.matches(mock)
    assert not result and result is sub_matcher.result


@pytest.mark.parametrize("matcher", (is_displayed, is_enabled, is_selected))
class TestIsSomething:
    def test_description(self, matcher):
        expected = matcher.__name__.replace("is_", "to be ")
        assert matcher().build_description(MatcherDescriptionTransformer()) == expected

    @pytest.mark.parametrize("expected", (True, False))
    def test_matches(self, matcher, expected):
        mock = MagicMock()
        mocked_method_name = matcher.__name__
        getattr(mock, mocked_method_name).return_value = expected
        assert bool(matcher().matches(mock)) is expected


def test_is_in_page():
    matcher = is_in_page()
    assert matcher.build_description(MatcherDescriptionTransformer()) == "to be present in page"
    assert matcher.matches(None)
