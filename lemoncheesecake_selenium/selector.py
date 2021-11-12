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
    DEFAULT_SCREENSHOT_ON_EXCEPTION = False
    DEFAULT_SCREENSHOT_ON_FAILED_CHECK = False

    def __init__(self, driver, *, timeout=None, screenshot_on_exception=None, screenshot_on_failed_check=None):
        self.driver = driver
        self.timeout = Selector.DEFAULT_TIMEOUT if timeout is None else timeout
        self.screenshot_on_exception = \
            Selector.DEFAULT_SCREENSHOT_ON_EXCEPTION if screenshot_on_exception is None else screenshot_on_exception
        self.screenshot_on_failed_check = \
            Selector.DEFAULT_SCREENSHOT_ON_FAILED_CHECK if screenshot_on_failed_check is None else screenshot_on_failed_check

    by_id = _selector(By.ID)
    by_xpath = _selector(By.XPATH)
    by_link_text = _selector(By.LINK_TEXT)
    by_partial_link_text = _selector(By.PARTIAL_LINK_TEXT)
    by_name = _selector(By.NAME)
    by_tag_name = _selector(By.TAG_NAME)
    by_class_name = _selector(By.CLASS_NAME)
    by_css_selector = _selector(By.CSS_SELECTOR)
