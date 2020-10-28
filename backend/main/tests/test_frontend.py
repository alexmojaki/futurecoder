from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DIR = Path(__file__).parent


def test_frontend(admin_user):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    try:
        _tests(driver, admin_user)
    except:
        driver.save_screenshot(str(DIR / "error_screenshot.png"))
        raise


def _tests(driver, admin_user):
    driver.get("http://localhost:3000/")

    # Open TOC
    driver.find_element_by_link_text("Go to the course").click()

    # Go to page
    driver.find_element_by_partial_link_text("Getting elements at a position").click()

    # Page redirects to login
    driver.find_element_by_css_selector("input[type=email]").send_keys(admin_user.email)
    driver.find_element_by_css_selector("input[type=password]").send_keys("password")
    driver.find_element_by_css_selector("button[type=submit]").click()

    sleep(2)
    print(driver.current_url)
