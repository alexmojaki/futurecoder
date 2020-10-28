from pathlib import Path
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
from selenium.webdriver.support.wait import WebDriverWait

DIR = Path(__file__).parent


def test_frontend():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    try:
        _tests(driver)
    except:
        driver.save_screenshot(str(DIR / "error_screenshot.png"))
        raise


def _tests(driver):
    driver.get("http://localhost:3000/")

    # Open TOC
    driver.find_element_by_link_text("Go to the course").click()

    # Go to page
    driver.find_element_by_partial_link_text("Getting elements at a position").click()

    # Page redirects to login
    # Use the credentials from init_db
    driver.find_element_by_css_selector("input[type=email]").send_keys(
        "admin@example.com"
    )
    driver.find_element_by_css_selector("input[type=password]").send_keys("admin")
    driver.find_element_by_css_selector("button[type=submit]").click()

    # Wait for page to load
    locator = (By.CSS_SELECTOR, ".book-text h1")
    WebDriverWait(driver, 10).until(text_to_be_present_in_element(locator, "Getting"))

    # Check title and beginning of text
    assert driver.find_element(*locator).text.startswith(
        "Getting elements at a position"
    )
    assert driver.find_element_by_css_selector(".book-text p").text.startswith(
        "Looping is great"
    )

    # Reverse until at first step
    button = driver.find_element_by_class_name("button-reverse-step")
    for _ in range(10):
        button.click()
        if (
            "In general, you can get the element"
            not in driver.find_element_by_css_selector(".book-text").text
        ):
            break
        sleep(0.1)
    else:
        pytest.fail()

    # Get code from instructions
    code = driver.find_element_by_css_selector("#step-text-0 pre").text
    assert (
        code
        == """\
words = ['This', 'is', 'a', 'list']

print(words[0])
print(words[1])
print(words[2])
print(words[3])"""
    )

    # Run code in editor
    driver.find_element_by_css_selector("#editor textarea").send_keys(code)
    driver.find_element_by_css_selector(".editor-buttons .btn-primary").click()

    # Check result in terminal
    locator = (By.CLASS_NAME, "terminal")
    WebDriverWait(driver, 10).until(text_to_be_present_in_element(locator, "This"))
    assert (
        driver.find_element(*locator).text
        == """\
This
is
a
list
>>> """
    )

    # Passed onto next step
    assert (
        "In general, you can get the element"
        in driver.find_element_by_css_selector(".book-text").text
    )
