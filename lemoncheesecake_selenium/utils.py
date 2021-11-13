from contextlib import contextmanager

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
import lemoncheesecake.api as lcc


def save_screenshot(driver: WebDriver, description: str = None):
    with lcc.prepare_image_attachment("screenshot.png", description=description) as path:
        driver.save_screenshot(path)


@contextmanager
def save_screenshot_on_exception(driver: WebDriver):
    try:
        yield
    except WebDriverException as exc:
        save_screenshot(driver, str(exc))
        raise
