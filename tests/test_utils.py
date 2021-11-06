from unittest.mock import MagicMock

import pytest
from callee import String

from lemoncheesecake_selenium import save_screenshot


@pytest.fixture
def prepare_image_attachment_mock(mocker):
    mock = mocker.patch("lemoncheesecake_selenium.utils.lcc.prepare_image_attachment")
    mock.return_value.__enter__.return_value = "/some/path"
    return mock


def test_save_screenshot(prepare_image_attachment_mock):
    driver_mock = MagicMock()
    save_screenshot(driver_mock)  # noqa
    prepare_image_attachment_mock.assert_called_with(String(), description=None)
    driver_mock.save_screenshot.assert_called_with("/some/path")


def test_save_screenshot_with_description(prepare_image_attachment_mock):
    driver_mock = MagicMock()
    save_screenshot(driver_mock, "my desc")  # noqa
    prepare_image_attachment_mock.assert_called_with(String(), description="my desc")
    driver_mock.save_screenshot.assert_called_with("/some/path")
