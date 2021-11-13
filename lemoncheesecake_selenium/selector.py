from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from lemoncheesecake_selenium.selection import Selection


def _selector(by):

    def builder(selector, value):
        return Selection(selector, by, value)
    builder.__doc__ = f"""
    Get a :py:class:`Selection` using element's {by}
    
    :param value: a value related to ``by`` 
    :return: :py:class:`Selection`
    """
    return builder


class Selector:
    """
    Factory of :py:class:`Selection` instances.
    """

    #: The default timeout value to use if no ``timeout`` argument is passed to ``Selector()``.
    #: This value can be overridden to set a global default timeout value for all :py:class:`Selection`
    #: instances.
    DEFAULT_TIMEOUT = 10
    #: The default boolean value to use if no ``screenshot_on_exceptions`` is passed to ``Selector()``.
    #: This value can be overridden to set a global screenshot on exceptions strategy for all :py:class:`Selection`
    #: instances.
    DEFAULT_SCREENSHOT_ON_EXCEPTIONS = False
    #: The default boolean value to use if no ``screenshot_on_failed_checks`` is passed to ``Selector()``.
    #: This value can be overridden to set a global screenshot on failed checks strategy for all :py:class:`Selection`
    #: instances.
    DEFAULT_SCREENSHOT_ON_FAILED_CHECKS = False

    def __init__(self, driver: WebDriver, *,
                 timeout: int = None,
                 screenshot_on_exceptions: bool = None, screenshot_on_failed_checks: bool = None):
        #: WebDriver
        self.driver = driver
        #: Timeout is later used as default timeout value in :py:class:`Selection` for the expected_condition mechanism.
        self.timeout = Selector.DEFAULT_TIMEOUT if timeout is None else timeout
        #: Whether or not the :py:class:`Selection` instances created with this selector will automatically
        #: save a screenshot upon ``WebDriverException`` exceptions on methods such as
        #: :py:func:`Selection.set_text`, :py:func:`Selection.click`, etc...
        self.screenshot_on_exceptions = \
            Selector.DEFAULT_SCREENSHOT_ON_EXCEPTIONS if screenshot_on_exceptions is None else screenshot_on_exceptions
        #: Whether or not the :py:class:`Selection` instances created with this selector will automatically
        #: save a screenshot upon failed checks with :py:func:`Selection.check_element`,
        #: :py:func:`Selection.require_element` and :py:func:`Selection.assert_element` methods.
        self.screenshot_on_failed_checks = \
            Selector.DEFAULT_SCREENSHOT_ON_FAILED_CHECKS if screenshot_on_failed_checks is None else screenshot_on_failed_checks

    by_id = _selector(By.ID)
    by_xpath = _selector(By.XPATH)
    by_link_text = _selector(By.LINK_TEXT)
    by_partial_link_text = _selector(By.PARTIAL_LINK_TEXT)
    by_name = _selector(By.NAME)
    by_tag_name = _selector(By.TAG_NAME)
    by_class_name = _selector(By.CLASS_NAME)
    by_css_selector = _selector(By.CSS_SELECTOR)
