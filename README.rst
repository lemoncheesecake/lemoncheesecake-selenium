lemoncheesecake-selenium
========================

.. image:: https://github.com/lemoncheesecake/lemoncheesecake-selenium/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/lemoncheesecake/lemoncheesecake-selenium/actions/workflows/tests.yml

.. image:: https://codecov.io/gh/lemoncheesecake/lemoncheesecake-selenium/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/lemoncheesecake/lemoncheesecake-selenium

.. image:: https://img.shields.io/pypi/v/lemoncheesecake-selenium.svg
    :target: https://pypi.org/project/lemoncheesecake-selenium/

.. image:: https://img.shields.io/pypi/pyversions/lemoncheesecake-selenium.svg
    :target: https://pypi.org/project/lemoncheesecake-selenium/

lemoncheesecake-selenium provides logging facilities to the `Selenium Python library <https://selenium-python.readthedocs.io/>`_ for
tests written with the `lemoncheesecake <http://lemoncheesecake.io>`_ test framework.

Here is a simple example of a search on https://www.python.org:

.. code-block:: python

    # suites/python_org_search.py

   import lemoncheesecake.api as lcc
   from lemoncheesecake.matching import *
   from lemoncheesecake_selenium import Selector, save_screenshot, is_in_page
   from selenium import webdriver
   from selenium.webdriver.common.keys import Keys

   @lcc.test()
   def python_org_search():
       driver = webdriver.Firefox()
       driver.implicitly_wait(10)
       driver.get("http://www.python.org")
       selector = Selector(driver)
       check_that("title", driver.title, contains_string("Python"))
       search_field = selector.by_name("q")
       search_field.clear()
       search_field.set_text("pycon")
       search_field.set_text(Keys.RETURN)
       selector.by_xpath("//h3[text()='Results']").check_element(is_in_page())
       save_screenshot(driver)
       driver.close()


We run the test:

.. code-block:: console

   $ lcc.py run
   ============================== python_org_search ==============================
    OK  1 # python_org_search.python_org_search

   Statistics :
    * Duration: 10s
    * Tests: 1
    * Successes: 1 (100%)
    * Failures: 0

   HTML report : file:///tmp/python_org_search/report/report.html

And here are the report details :

.. image:: https://github.com/lemoncheesecake/lemoncheesecake-selenium/blob/master/doc/_static/report-sample.png?raw=true
    :alt: test result

Installation
------------

Install through pip:

.. code-block:: console

   $ pip install lemoncheesecake-selenium

lemoncheesecake-selenium is compatible with Python 3.7-3.10 and Selenium 4.x.

You will also need to `install a WebDriver <https://www.selenium.dev/documentation/getting_started/installing_browser_drivers/>`_
to control your web browser.

Features
--------

- clicking, setting text, selecting element in a SELECT, etc..

- checking DOM nodes

- screenshots

Documentation
-------------

The documentation is available on https://lemoncheesecake-selenium.readthedocs.io.


Contact
-------

Bug reports and improvement ideas are welcomed in tickets.
A Google Groups forum is also available for discussions about lemoncheesecake:
https://groups.google.com/forum/#!forum/lemoncheesecake.
