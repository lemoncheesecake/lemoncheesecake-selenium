from typing import Union

from selenium.webdriver.remote.webelement import WebElement
from lemoncheesecake.matching.matcher import Matcher, MatchResult, MatcherDescriptionTransformer
from lemoncheesecake.matching import *


class HasText(Matcher):
    def __init__(self, matcher):
        self.matcher = matcher

    def build_description(self, transformation):
        return transformation(
            "to have text that %s" % self.matcher.build_description(
                MatcherDescriptionTransformer(conjugate=True)
            )
        )

    def matches(self, actual: WebElement):
        return self.matcher.matches(actual.text)


def has_text(expected: Union[Matcher, str]):
    """
    Test if ``WebElement`` instance has text.

    :param expected: expected text
    :return: ``Matcher`` instance
    """
    return HasText(is_(expected))


class EntityMatcher(Matcher):
    def __init__(self, entity, name, func, matcher):
        self.entity = entity
        self.name = name
        self.func = func
        self.matcher = matcher

    def build_description(self, transformation):
        description = transformation(f"to have {self.entity} '{self.name}'")
        if self.matcher:
            description += " that %s" % self.matcher.build_description(
                MatcherDescriptionTransformer(conjugate=True)
            )
        return description

    def matches(self, actual: WebElement):
        value = self.func(actual)
        if value is None:
            return MatchResult.failure(f"Element does not have {self.entity} '{self.name}'")

        if self.matcher:
            return self.matcher.matches(value)
        else:
            return MatchResult.success()


def has_attribute(name: str, matcher: Union[str, Matcher] = None):
    """
    Test if ``WebElement`` element has entity.

    :param name: attribute name
    :param matcher: attribute matcher
    :return: ``Matcher`` instance
    """

    return EntityMatcher(
        "attribute",
        name,
        lambda actual: actual.get_attribute(name),
        is_(matcher) if matcher is not None else None
    )


def has_property(name, matcher: Union[str, Matcher] = None):
    return EntityMatcher(
        "property",
        name,
        lambda actual: actual.get_property(name),
        is_(matcher) if matcher is not None else None
    )


class StateMatcher(Matcher):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def build_description(self, transformation):
        return transformation(f"to be {self.name}")

    def matches(self, actual: WebElement):
        return MatchResult(self.func(actual))


def is_displayed():
    """
    Test if ``WebElement`` element is displayed.

    :return: :py:class:`Matcher <lemoncheesecake.matching.matcher.Matcher>` instance
    """
    return StateMatcher("displayed", lambda actual: actual.is_displayed())


def is_enabled():
    """
    Test if ``WebElement`` element is enabled.

    :return: :py:class:`Matcher <lemoncheesecake.matching.matcher.Matcher>` instance
    """
    return StateMatcher("enabled", lambda actual: actual.is_enabled())


def is_selected():
    """
    Test if ``WebElement`` element is selected.

    :return: :py:class:`Matcher <lemoncheesecake.matching.matcher.Matcher>` instance
    """
    return StateMatcher("selected", lambda actual: actual.is_selected())


class IsInPage(Matcher):
    def build_description(self, transformation):
        return transformation("to be present in page")

    def matches(self, _):
        return MatchResult.success()


def is_in_page():
    """
    Test if ``WebElement`` is present in page.

    NB: as the matcher is already called with a ``WebElement`` instance,
    the matcher will always be successful.

    :return: :py:class:`Matcher <lemoncheesecake.matching.matcher.Matcher>` instance
    """
    return IsInPage()
