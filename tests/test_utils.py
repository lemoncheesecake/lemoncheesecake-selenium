from unittest.mock import MagicMock

import pytest
from callee import String, Any, Contains
from selenium.common.exceptions import WebDriverException

from lemoncheesecake_selenium import save_screenshot, save_screenshot_on_exception


ATTACHMENT_PATH = "/some/path"


@pytest.fixture
def prepare_image_attachment_mock(mocker):
    mock = mocker.patch("lemoncheesecake.api.prepare_image_attachment")
    mock.return_value.__enter__.return_value = ATTACHMENT_PATH
    return mock


def test_save_screenshot(prepare_image_attachment_mock):
    driver_mock = MagicMock()
    save_screenshot(driver_mock)  # noqa
    prepare_image_attachment_mock.assert_called_with(String(), description=None)
    driver_mock.save_screenshot.assert_called_with(ATTACHMENT_PATH)


def test_save_screenshot_with_description(prepare_image_attachment_mock):
    driver_mock = MagicMock()
    save_screenshot(driver_mock, "my desc")  # noqa
    prepare_image_attachment_mock.assert_called_with(String(), description="my desc")
    driver_mock.save_screenshot.assert_called_with(ATTACHMENT_PATH)


def test_save_screenshot_on_exception(prepare_image_attachment_mock):
    driver_mock = MagicMock()
    with pytest.raises(WebDriverException):
        with save_screenshot_on_exception(driver_mock):  # noqa
            raise WebDriverException("some error")

    prepare_image_attachment_mock.assert_called_with(String(), description=Contains("some error"))
    driver_mock.save_screenshot.assert_called_with(Any())


def test_save_screenshot_on_exception_without_exception(prepare_image_attachment_mock):
    driver_mock = MagicMock()
    with save_screenshot_on_exception(driver_mock):  # noqa
        pass

    driver_mock.save_screenshot.assert_not_called()

