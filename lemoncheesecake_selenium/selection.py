from __future__ import annotations

from typing import Sequence
from contextlib import contextmanager

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, require_that, assert_that
from lemoncheesecake.matching.matcher import Matcher, MatchResult, MatcherDescriptionTransformer

from lemoncheesecake_selenium.utils import save_screenshot, save_screenshot_on_exception


class HasElement(Matcher):
    def __init__(self, matcher: Matcher):
        super().__init__()
        self.matcher = matcher

    def build_description(self, transformation):
        return self.matcher.build_description(transformation)

    def _matches(self, actual: Selection) -> MatchResult:
        try:
            element = actual.element
        except NoSuchElementException:
            return MatchResult.failure(f"Could not find {actual}")
        return self.matcher.matches(element)

    def _build_failure_msg(self, actual: Selection, result: MatchResult):
        failure_msg = "Expect %s %s" % (
            actual, self.matcher.build_description(MatcherDescriptionTransformer())
        )
        if result.description:
            failure_msg += ": " + result.description
        return failure_msg

    def matches(self, actual: Selection) -> MatchResult:
        result = self._matches(actual)
        if not result and actual.selector.screenshot_on_failed_check:
            save_screenshot(actual.driver, self._build_failure_msg(actual, result))

        return result


class Selection:
    def __init__(self, selector, by, value):
        from .selector import Selector  # workaround for circular import
        self.selector: Selector = selector
        self.by = by
        self.value = value
        self._expected_condition = None
        self._expected_condition_timeout = 0
        self._expected_condition_extra_args = ()
        self._expected_condition_reverse = False

    @property
    def driver(self) -> WebDriver:
        return self.selector.driver

    @property
    def locator(self):
        return self.by, self.value

    def _must_be_waited(self, expected_condition, timeout, extra_args, reverse):
        self._expected_condition = expected_condition
        self._expected_condition_timeout = timeout if timeout is not None else self.selector.timeout
        self._expected_condition_extra_args = extra_args
        self._expected_condition_reverse = reverse
        return self

    def must_be_waited_until(self, expected_condition, timeout=None, extra_args=()):
        return self._must_be_waited(expected_condition, timeout, extra_args, reverse=False)

    def must_be_waited_until_not(self, expected_condition, timeout=None, extra_args=()):
        return self._must_be_waited(expected_condition, timeout, extra_args, reverse=True)

    def _wait_expected_condition(self):
        if not self._expected_condition:
            return

        wait_method = getattr(
            WebDriverWait(self.driver, self._expected_condition_timeout),
            "until_not" if self._expected_condition_reverse else "until"
        )
        wait_method(
            self._expected_condition(self.locator, *self._expected_condition_extra_args),
            message="expected condition has not been fulfilled"
        )

    @contextmanager
    def _exception_handler(self):
        if self.selector.screenshot_on_exception:
            with save_screenshot_on_exception(self.driver):
                yield
        else:
            yield

    @property
    def element(self) -> WebElement:
        self._wait_expected_condition()
        return self.driver.find_element(self.by, self.value)

    @property
    def elements(self) -> Sequence[WebElement]:
        self._wait_expected_condition()
        return self.driver.find_elements(self.by, self.value)

    def click(self):
        lcc.log_info(f"Click on {self}")
        with self._exception_handler():
            self.element.click()

    def clear(self):
        lcc.log_info(f"Clear {self}")
        with self._exception_handler():
            self.element.clear()

    def set_text(self, text: str):
        lcc.log_info(f"Set text '{text}' on {self}")
        with self._exception_handler():
            self.element.send_keys(text)

    def check_element(self, expected):
        check_that(str(self), self, HasElement(expected))

    def require_element(self, expected):
        require_that(str(self), self, HasElement(expected))

    def assert_element(self, expected):
        assert_that(str(self), self, HasElement(expected))

    def save_screenshot(self, description: str = None):
        if description is None:
            description = f"Screenshot of {self}"

        with lcc.prepare_image_attachment("screenshot.png", description) as path:
            self.element.screenshot(path)

    def _select(self, method_name, value=NotImplemented):
        # Build contextual info for logs
        action_label = method_name.replace("_", " ")
        if value is not NotImplemented:
            action_label += " " + repr(value)

        lcc.log_info(f"{action_label} the {self}".capitalize())

        with self._exception_handler():
            select = Select(self.element)
            if value is NotImplemented:
                getattr(select, method_name)()
            else:
                getattr(select, method_name)(value)

    def select_by_value(self, value):
        self._select("select_by_value", value)

    def select_by_index(self, index):
        self._select("select_by_index", index)

    def select_by_visible_text(self, text):
        self._select("select_by_visible_text", text)

    def deselect_all(self):
        self._select("deselect_all")

    def deselect_by_index(self, index):
        self._select("deselect_by_index", index)

    def deselect_by_value(self, value):
        self._select("deselect_by_value", value)

    def deselect_by_visible_text(self, text):
        self._select("deselect_by_visible_text", text)

    def __str__(self):
        if self.by == By.XPATH:
            by = "XPATH"
        elif self.by == By.CSS_SELECTOR:
            by = "CSS selector"
        else:
            by = self.by

        return f"element identified by {by} '{self.value}'"
