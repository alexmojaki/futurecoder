from pathlib import Path
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    # Empty shell
    await_result(driver, "", ">>> ")

    # Run code in shell, check result
    driver.find_element_by_css_selector(".terminal input").send_keys("12345\n")
    await_result(
        driver,
        "",
        """\
>>> 12345
12345
>>> """,
    )

    # Check title and beginning of text
    assert driver.find_element(*locator).text.startswith(
        "Getting elements at a position"
    )
    assert driver.find_element_by_css_selector(".book-text p").text.startswith(
        "Looping is great"
    )

    # Reverse until at first step
    reverse_button = driver.find_element_by_class_name("button-reverse-step")
    skip_button = driver.find_element_by_class_name("button-skip-step")
    for _ in range(10):
        reverse_button.click()
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
    editor = driver.find_element_by_css_selector("#editor textarea")
    run_button = driver.find_element_by_css_selector(".editor-buttons .btn-primary")
    snoop_button = driver.find_element_by_css_selector(".editor-buttons .btn-success")
    run_code(editor, run_button, code)

    # Check result in terminal
    await_result(
        driver,
        "This",
        """\
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

    # Run with snoop
    snoop_button.click()
    await_result(
        driver,
        "print",
        """\
    1 | words = ['This', 'is', 'a', 'list']
 ...... len(words) = 4
    3 | print(words[0])
This
    4 | print(words[1])
is
    5 | print(words[2])
a
    6 | print(words[3])
list
>>> """
    )

    # No hint button present
    assert not driver.find_elements_by_class_name("hint-icon")

    # Skip forward to exercise
    for _ in range(3):
        skip_button.click()
        sleep(0.1)

    assert (
        "Let's get some exercise!"
        in driver.find_element_by_css_selector(".book-text").text
    )

    show_hints_and_solution(driver, num_hints=9, parsons=False)

    # Hidden solution contains correct text
    code = driver.find_element_by_css_selector(".gradual-solution code")
    assert (
        code.text
        == """\
for i in range(len(things)):
    if to_find == things[i]:
        print(i)
        break"""
    )

    # Click button repeatedly to reveal solution
    get_hint_button = driver.find_element_by_css_selector(".hints-popup .btn-primary")
    assert get_hint_button.text == "Reveal"
    for i in range(25):
        assert len(code.find_elements_by_class_name("solution-token-hidden")) == 25 - i
        assert len(code.find_elements_by_class_name("solution-token-visible")) == 12 + i
        get_hint_button.click()

    # Click outside hints popup to close
    driver.find_element_by_class_name("popup-overlay").click()

    # No messages visible
    assert not driver.find_elements_by_class_name("book-message")

    # Run code which triggers a message
    # Here we leave out indentation because ace adds some
    run_code(editor, run_button, """\
things = ['on', 'the', 'way', 'to', 'the', 'store']
to_find = 'the'

for i in range(len(things)):
if to_find == things[i]:
print(i)
""")

    # Now we have a message
    assert (
        driver.find_element_by_css_selector(".book-message .card-body").text
        == "You're almost there! However, this prints all the indices, not just the first one."
    )

    # Fix the solution
    editor.send_keys("        break")
    run_button.click()
    sleep(0.2)

    # Step has passed, message has disappeared
    assert not driver.find_elements_by_class_name("book-message")

    # Skip to zip_longest exercise
    skip_button.click()

    # This exercise has a Parsons problem
    show_hints_and_solution(driver, num_hints=10, parsons=True)

    assert {
        node.text
        for node in driver.find_elements_by_css_selector(".parsons-droppable code")
    } == set(
        """\
length1 = len(string1)
length2 = len(string2)
if length1 > length2:
    length = length1
else:
    length = length2
for i in range(length):
    if i < len(string1):
        char1 = string1[i]
    else:
        char1 = ' '
    if i < len(string2):
        char2 = string2[i]
    else:
        char2 = ' '
    print(char1 + ' ' + char2)""".splitlines()
    )


def show_hints_and_solution(driver, *, num_hints, parsons):
    # No hints popup visible
    assert not driver.find_elements_by_class_name("hints-popup")

    # Click hint lightbulb
    driver.find_element_by_class_name("hint-icon").click()

    # Show all hints
    for hint_num in range(num_hints):
        assert len(driver.find_elements_by_class_name("hint-body")) == hint_num
        get_hint_button = driver.find_element_by_css_selector(
            ".hints-popup .btn-primary"
        )
        assert get_hint_button.text == (
            "Get a hint" if hint_num == 0 else "Get another hint"
        )
        get_hint_button.click()

    # All hints are shown
    assert len(driver.find_elements_by_class_name("hint-body")) == num_hints

    # Click 'Show solution'
    get_hint_button = driver.find_element_by_css_selector(".hints-popup .btn-primary")
    assert get_hint_button.text == ("Show shuffled solution" if parsons else "Show solution")
    get_hint_button.click()

    # Solution not yet visible
    assert not driver.find_elements_by_css_selector(".gradual-solution")
    assert not driver.find_elements_by_css_selector(".parsons-droppable")

    # Are you sure? Click 'Yes'
    get_hint_button = driver.find_element_by_css_selector(".hints-popup .btn-primary")
    assert get_hint_button.text == "Yes"
    get_hint_button.click()

    # Exactly one kind of solution visible
    assert bool(driver.find_elements_by_css_selector(".gradual-solution")) == (not parsons)
    assert bool(driver.find_elements_by_css_selector(".parsons-droppable")) == parsons


def run_code(editor, run_button, text):
    editor.send_keys(Keys.CONTROL + "a")
    editor.send_keys(Keys.BACK_SPACE)
    editor.send_keys(text)
    run_button.click()


def await_result(driver, part, full):
    locator = (By.CLASS_NAME, "terminal")

    WebDriverWait(driver, 10).until(text_to_be_present_in_element(locator, part))
    assert driver.find_element(*locator).text == full
