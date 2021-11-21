from __future__ import annotations

from typing import Sequence, Callable
from contextlib import contextmanager

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, require_that, assert_that, not_
from lemoncheesecake.matching.matcher import Matcher, MatchResult, MatcherDescriptionTransformer

from lemoncheesecake_selenium.matchers import is_in_page
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
        if not result and actual.screenshot_on_failed_checks:
            save_screenshot(actual.driver, self._build_failure_msg(actual, result))

        return result


class Selection:
    #: The default timeout value to use if no ``timeout`` argument is passed to
    #: the :py:func:`must_be_waited_until` / :py:func:`must_be_waited_until_not` methods.
    default_timeout = 10
    #: Whether or not a screenshot will be automatically saved upon
    #: upon ``WebDriverException`` exceptions on methods such as
    #: :py:func:`Selection.set_text`, :py:func:`Selection.click`, etc...
    screenshot_on_exceptions = False
    #: Whether or not a screenshot will be automatically saved upon failed checks
    #: with :py:func:`Selection.check_element`,
    #: :py:func:`Selection.require_element` and :py:func:`Selection.assert_element` methods.
    screenshot_on_failed_checks = False

    def __init__(self, driver, by, value):
        from .selector import Selector  # workaround for circular import
        self.driver = driver
        self.by = by
        self.value = value
        self._expected_condition = None
        self._expected_condition_timeout = 0
        self._expected_condition_extra_args = ()
        self._expected_condition_reverse = False

    @property
    def locator(self):
        return self.by, self.value

    def _must_be_waited(self, expected_condition, timeout, extra_args, reverse):
        self._expected_condition = expected_condition
        self._expected_condition_timeout = timeout if timeout is not None else self.default_timeout
        self._expected_condition_extra_args = extra_args
        self._expected_condition_reverse = reverse
        return self

    def must_be_waited_until(self, expected_condition: Callable, *, timeout: int = None, extra_args=()):
        """
        The method can be called to set an explicit wait
        (see https://selenium-python.readthedocs.io/waits.html#explicit-waits) on the underlying element
        so that it is considered available when the ``expected_condition`` is met.

        :param expected_condition: a callable that will take a locator (a tuple of ``(by, path)``) as first argument
        :param timeout: wait timeout (will be :py:attr:`Selection.default_timeout` if no argument is passed)
        :param extra_args: extra arguments to be passed to the ``expected_condition`` callable
        :return: ``self``, meaning this method can be chain called
        """
        return self._must_be_waited(expected_condition, timeout, extra_args, reverse=False)

    def must_be_waited_until_not(self, expected_condition: Callable, *, timeout: int = None, extra_args=()):
        """
        The method can be called to set an explicit wait
        (see https://selenium-python.readthedocs.io/waits.html#explicit-waits) on the underlying element
        so that it is considered available when the ``expected_condition`` is NOT met.

        :param expected_condition: a callable that will take a locator (a tuple of ``(by, path)``) as first argument
        :param timeout: wait timeout (will be :py:attr:`Selection.default_timeout` if no argument is passed)
        :param extra_args: extra arguments to be passed to the ``expected_condition`` callable
        :return: ``self``, meaning this method can be chain called
        """
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
        if self.screenshot_on_exceptions:
            with save_screenshot_on_exception(self.driver):
                yield
        else:
            yield

    @property
    def element(self) -> WebElement:
        """
        :return: the underlying ``WebElement`` with the explicit wait taken into account (if any has been set)
        """
        self._wait_expected_condition()
        return self.driver.find_element(self.by, self.value)

    @property
    def elements(self) -> Sequence[WebElement]:
        """
        :return: the underlying ``WebElement`` list with the explicit wait taken into account (if any has been set)
        """
        self._wait_expected_condition()
        return self.driver.find_elements(self.by, self.value)

    def click(self):
        """
        Click on the element.
        """
        lcc.log_info(f"Click on {self}")
        with self._exception_handler():
            self.element.click()

    def clear(self):
        """
        Clear the element.
        """
        lcc.log_info(f"Clear {self}")
        with self._exception_handler():
            self.element.clear()

    def set_text(self, text: str):
        """
        Set to text in the element.

        :param text: text to be set
        """
        lcc.log_info(f"Set text '{text}' on {self}")
        with self._exception_handler():
            self.element.send_keys(text)

    def check_element(self, expected: Matcher):
        """
        Check that the element matches ``expected`` using
        the :py:func:`lemoncheesecake.matching.check_that` function.

        :param expected: a ``Matcher`` instance whose ``matches`` method will be called with
            the ``WebElement`` that has been found
        """
        check_that(str(self), self, HasElement(expected))

    def check_no_element(self):
        """
        Check that the element is not present using
        the :py:func:`lemoncheesecake.matching.check_that` function.
        """
        check_that(str(self), self, not_(HasElement(is_in_page())))

    def require_element(self, expected: Matcher):
        """
        Check that the element matches ``expected`` using
        the :py:func:`lemoncheesecake.matching.require_that` function.

        :param expected: a ``Matcher`` instance whose ``matches`` method will be called with
            the ``WebElement`` that has been found
        """
        require_that(str(self), self, HasElement(expected))

    def require_no_element(self):
        """
        Check that the element is not present using
        the :py:func:`lemoncheesecake.matching.require_that` function.
        """
        require_that(str(self), self, not_(HasElement(is_in_page())))

    def assert_element(self, expected: Matcher):
        """
        Check that the element matches ``expected`` using
        the :py:func:`lemoncheesecake.matching.assert_that` function.

        :param expected: a ``Matcher`` instance whose ``matches`` method will be called with
            the ``WebElement`` that has been found
        """
        assert_that(str(self), self, HasElement(expected))

    def assert_no_element(self):
        """
        Check that the element is not present using
        the :py:func:`lemoncheesecake.matching.assert_that` function.
        """
        assert_that(str(self), self, not_(HasElement(is_in_page())))

    def save_screenshot(self, description: str = None):
        """
        Take and save (as lemoncheesecake attachment) a screenshot of the underlying element.

        :param description: description of the image attachment for that screenshot
        """
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
        """
        Select option by its value considering the underlying element is a SELECT element.

        :param value: the value to be selected
        """
        self._select("select_by_value", value)

    def select_by_index(self, index):
        """
        Select option by its index considering the underlying element is a SELECT element.

        :param index: the index to be selected
        """
        self._select("select_by_index", index)

    def select_by_visible_text(self, text):
        """
        Select option by its text considering the underlying element is a SELECT element.

        :param text: the text to be selected
        """
        self._select("select_by_visible_text", text)

    def deselect_all(self):
        """
        Deselect all options considering the underlying element is a SELECT element.
        """
        self._select("deselect_all")

    def deselect_by_value(self, value):
        """
        Deselect option by its value considering the underlying element is a SELECT element.

        :param value: the value to be deselected
        """
        self._select("deselect_by_value", value)

    def deselect_by_index(self, index):
        """
        Deselect option by its index considering the underlying element is a SELECT element.

        :param index: the index to be deselected
        """
        self._select("deselect_by_index", index)

    def deselect_by_visible_text(self, text):
        """
        Deselect option by its text considering the underlying element is a SELECT element.

        :param text: the text to be deselected
        """
        self._select("deselect_by_visible_text", text)

    def __str__(self):
        if self.by == By.XPATH:
            by = "XPATH"
        elif self.by == By.CSS_SELECTOR:
            by = "CSS selector"
        else:
            by = self.by

        return f"element identified by {by} '{self.value}'"
