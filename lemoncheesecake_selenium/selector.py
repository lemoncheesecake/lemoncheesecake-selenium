from selenium.webdriver.common.by import By

from lemoncheesecake_selenium.selection import Selection


def _selector(by):
    def builder(locator, value):
        return Selection(locator.driver, by, value)
    builder.__doc__ = f"""
    Get a :py:class:`Selection` using element's {by}
    
    :param value: a value related to ``by`` 
    :return: :py:class:`Location`
    """
    return builder


class Selector:
    def __init__(self, driver):
        self.driver = driver

    by_id = _selector(By.ID)
    by_xpath = _selector(By.XPATH)
    by_link_text = _selector(By.LINK_TEXT)
    by_partial_link_text = _selector(By.PARTIAL_LINK_TEXT)
    by_name = _selector(By.NAME)
    by_tag_name = _selector(By.TAG_NAME)
    by_class_name = _selector(By.TAG_NAME)
    by_css_selector = _selector(By.CSS_SELECTOR)