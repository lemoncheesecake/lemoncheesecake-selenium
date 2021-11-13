from selenium.webdriver.common.by import By
from lemoncheesecake_selenium.selection import Selection


def _selector(by):

    def builder(selector, value):
        return Selection(selector, by, value)
    builder.__doc__ = f"""
    Get a :py:class:`Selection` using element's {by}
    
    :param value: a value related to ``by`` 
    :return: :py:class:`Location`
    """
    return builder


class Selector:
    DEFAULT_TIMEOUT = 10
    DEFAULT_SCREENSHOT_ON_EXCEPTIONS = False
    DEFAULT_SCREENSHOT_ON_FAILED_CHECKS = False

    def __init__(self, driver, *, timeout=None, screenshot_on_exceptions=None, screenshot_on_failed_checks=None):
        self.driver = driver
        self.timeout = Selector.DEFAULT_TIMEOUT if timeout is None else timeout
        self.screenshot_on_exceptions = \
            Selector.DEFAULT_SCREENSHOT_ON_EXCEPTIONS if screenshot_on_exceptions is None else screenshot_on_exceptions
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
