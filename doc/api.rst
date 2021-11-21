.. _`api`:

API Reference
=============

API compatibility / stability
-----------------------------

lemoncheesecake-selenium follows the well know `Semantic Versioning <https://semver.org/>`_ for its public API.
Since lemoncheesecake-selenium is still on 0.y.z major version, API breaking changes might occur; it is then advised to
pin the version.

What is considered as "public" is everything documented on https://lemoncheesecake-selenium.readthedocs.io.
Everything else is internal and is subject to changes at anytime.

.. module:: lemoncheesecake_selenium


Selector
--------

.. autoclass:: Selector
    :members: by_id, by_xpath, by_link_text, by_partial_link_text, by_name, by_tag_name, by_class_name,
        by_css_selector


Selection
---------

.. autoclass:: Selection
    :members: default_timeout, screenshot_on_exceptions, screenshot_on_failed_checks,
        must_be_waited_until, must_be_waited_until_not,
        element, elements, click, clear, set_text,
        select_by_value, select_by_index, select_by_visible_text,
        deselect_all, deselect_by_value, deselect_by_index, deselect_by_visible_text,
        save_screenshot,
        check_element, check_no_element,
        require_element, require_no_element,
        assert_element, assert_no_element


Matchers
--------

.. autofunction:: is_in_page
.. autofunction:: has_text
.. autofunction:: has_attribute
.. autofunction:: has_property
.. autofunction:: is_displayed
.. autofunction:: is_enabled
.. autofunction:: is_selected

Utils
--------

.. autofunction:: save_screenshot
.. autofunction:: save_screenshot_on_exception
