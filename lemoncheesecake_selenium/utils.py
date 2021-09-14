from selenium.webdriver.remote.webdriver import WebDriver
import lemoncheesecake.api as lcc


def save_screenshot(driver: WebDriver, description: str = None):
    with lcc.prepare_image_attachment("screenshot.png", description=description) as path:
        driver.save_screenshot(path)
