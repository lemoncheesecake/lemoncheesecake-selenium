from typing import Sequence

from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, require_that, assert_that
from lemoncheesecake.matching.matcher import Matcher, MatchResult, MatcherDescriptionTransformer


class HasElement(Matcher):
    def __init__(self, matcher: Matcher):
        super().__init__()
        self.matcher = matcher

    def build_description(self, transformation):
        return self.matcher.build_description(transformation)

    def matches(self, actual: "Location"):
        try:
            element = actual.get_element()
        except NoSuchElementException as exc:
            return MatchResult.failure(f"Could not find {actual!r}")
        return self.matcher.matches(element)


class Location:
    def __init__(self, driver, by, value):
        self.driver = driver
        self.by = by
        self.value = value

    def get_element(self) -> WebElement:
        return self.driver.find_element(self.by, self.value)

    def get_elements(self) -> Sequence[WebElement]:
        return self.driver.find_elements(self.by, self.value)

    def click(self):
        try:
            element = self.get_element()
            element.click()
        except WebDriverException as exc:
            raise lcc.AbortTest(f"Could not click on {self!r}: {exc}")
        lcc.log_info(f"Click on {self!r}")

    def clear(self):
        try:
            element = self.get_element()
            element.clear()
        except WebDriverException as exc:
            raise lcc.AbortTest(f"Could not clear {self!r}: {exc}")
        lcc.log_info(f"Clear {self!r}")

    def set_text(self, text: str):
        try:
            element = self.get_element()
            element.send_keys(text)
        except WebDriverException as exc:
            raise lcc.AbortTest(f"Could not set text '{text}' on {self!r}: {exc}")
        lcc.log_info(f"Set text '{text}' on {self!r}")

    def check_element(self, *expectations):
        for expected in expectations:
            check_that(repr(self), self, HasElement(expected))

    def require_element(self, *expectations):
        for expected in expectations:
            require_that(repr(self), self, HasElement(expected))

    def assert_element(self, *expectations):
        for expected in expectations:
            assert_that(repr(self), self, HasElement(expected))

    def __repr__(self):
        return f"element identified by {self.by} '{self.value}'"
