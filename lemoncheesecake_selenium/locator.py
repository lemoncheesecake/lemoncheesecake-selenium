from selenium.webdriver.common.by import By

from lemoncheesecake_selenium.location import Location


def _location_builder(by):
    def builder(locator, value):
        return Location(locator.driver, by, value)
    builder.__doc__ = f"""
    Get a location using element {by}
    
    :param value: a value related to ``by`` 
    :return: :py:class:`Location`
    """
    return builder


class Locator:
    def __init__(self, driver):
        self.driver = driver

    by_id = _location_builder(By.ID)
    by_xpath = _location_builder(By.XPATH)
    by_link_text = _location_builder(By.LINK_TEXT)
    by_partial_link_text = _location_builder(By.PARTIAL_LINK_TEXT)
    by_name = _location_builder(By.NAME)
    by_tag_name = _location_builder(By.TAG_NAME)
    by_class_name = _location_builder(By.TAG_NAME)
    by_css_selector = _location_builder(By.CSS_SELECTOR)
