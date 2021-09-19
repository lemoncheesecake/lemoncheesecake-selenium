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


def has_text(expected):
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


def has_attribute(name, matcher=None):
    return EntityMatcher(
        "attribute",
        name,
        lambda actual: actual.get_attribute(name),
        is_(matcher) if matcher is not None else None
    )


def has_property(name, matcher=None):
    return EntityMatcher(
        "property",
        name,
        lambda actual: actual.get_property(name),
        is_(matcher) if matcher is not None else None
    )


class IsDisplayed(Matcher):
    def build_description(self, transformation):
        return transformation("to be displayed")

    def matches(self, actual: WebElement):
        return MatchResult(actual.is_displayed())


def is_displayed():
    return IsDisplayed()


class IsEnabled(Matcher):
    def build_description(self, transformation):
        return transformation("to be enabled")

    def matches(self, actual: WebElement):
        return MatchResult(actual.is_enabled())


def is_enabled():
    return IsEnabled()


class IsSelected(Matcher):
    def build_description(self, transformation):
        return transformation("to be selected")

    def matches(self, actual: WebElement):
        return MatchResult(actual.is_selected())


def is_selected():
    return IsSelected()
