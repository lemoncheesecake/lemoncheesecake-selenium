from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from lemoncheesecake_selenium.selection import Selection


def _selector(by):

    def builder(selector, value):
        return Selection(selector.driver, by, value)
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

    def __init__(self, driver: WebDriver):
        #: WebDriver
        self.driver = driver

    by_id = _selector(By.ID)
    by_xpath = _selector(By.XPATH)
    by_link_text = _selector(By.LINK_TEXT)
    by_partial_link_text = _selector(By.PARTIAL_LINK_TEXT)
    by_name = _selector(By.NAME)
    by_tag_name = _selector(By.TAG_NAME)
    by_class_name = _selector(By.CLASS_NAME)
    by_css_selector = _selector(By.CSS_SELECTOR)
