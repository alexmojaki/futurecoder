import os
import sys
from pathlib import Path
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element, invisibility_of_element
from selenium.webdriver.support.wait import WebDriverWait

del sys.modules["urllib3"]  # so that stub_module doesn't complain

this_dir = Path(__file__).parent
assets_dir = this_dir / "test_frontend_assets"
assets_dir.mkdir(exist_ok=True)

sauce_tunnel = os.environ.get("SAUCE_TUNNEL")


def get_driver(caps):
    if sauce_tunnel:
        desired_capabilities = {
            **caps,
            "sauce:options": {
                "tunnelName": sauce_tunnel,
                "name": "futurecoder",
            },
        }
        url = "https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com:443/wd/hub".format(
            **os.environ
        )
        driver = webdriver.Remote(
            command_executor=url,
            desired_capabilities=desired_capabilities,
        )
    else:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)
    driver.implicitly_wait(5)
    return driver


def params():
    if not sauce_tunnel:
        yield None
        return
    for os_name, extra_browser, os_versions in [
        ["Windows", "MicrosoftEdge", ["11", "10"]],
        ["macOS", "Safari", ["12", "11.00"]],
    ]:
        for os_version in os_versions[:1]:  # TODO use all versions
            for browser in ["Chrome", "Firefox", extra_browser]:
                caps = dict(
                    platform=f"{os_name} {os_version}",
                    version="latest",
                    browserName=browser,
                )
                if browser == "Safari" and os_version == "12":
                    yield caps | {"version": "15"}
                else:
                    yield caps
                return  # TODO


@pytest.mark.parametrize("caps", list(params()))
def test_frontend(caps):
    driver = get_driver(caps)
    status = "failed"
    try:
        _tests(driver)
        status = "passed"
    finally:
        if sauce_tunnel:
            driver.execute_script(f"sauce:job-result={status}")
        try:
            driver.save_screenshot(str(assets_dir / "screenshot.png"))
            (assets_dir / "logs.txt").write_text(
                "\n".join(entry["message"] for entry in driver.get_log("browser"))
            )
            (assets_dir / "page_source.html").write_text(driver.page_source)
            (assets_dir / "state.json").write_text(
                driver.execute_script("return JSON.stringify(reduxStore.getState())")
            )
        finally:
            driver.quit()


def _tests(driver):
    driver.get("http://localhost:3000/course/#toc")

    # Go to page
    driver.find_element(By.PARTIAL_LINK_TEXT, "Getting elements at a position").click()

    # Wait for page to load
    locator = (By.CSS_SELECTOR, ".book-text h1")
    WebDriverWait(driver, 10).until(text_to_be_present_in_element(locator, "Getting"))

    # Check title and beginning of text
    assert driver.find_element(*locator).text.startswith(
        "Getting elements at a position"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".book-text p").text.startswith(
        "Looping is great"
    )

    # Reverse buttons don't exist (developer mode is off)
    assert not driver.find_elements(By.CLASS_NAME, "button-reverse-step"), "Is developer mode on?"

    assert driver.find_element(By.CLASS_NAME, "navbar").text.strip() == "Login / Sign up\nTable of Contents"

    # Click on menu
    driver.find_element(By.CSS_SELECTOR, ".nav-item.custom-popup").click()
    assert (
        driver.find_element(By.CLASS_NAME, "menu-popup").text
        == """\
Sign out
Settings
Feedback
Español
Français
தமிழ்"""
    )

    # Open settings
    settings_button = driver.find_element(By.CSS_SELECTOR, ".menu-popup .btn.btn-primary")
    assert settings_button.text.strip() == "Settings"
    settings_button.click()

    # Turn on developer mode
    developer_mode_togle = driver.find_element(By.CSS_SELECTOR, ".settings-modal label")
    developer_mode_togle.click()

    # Reverse buttons exist now
    reverse_button = driver.find_element(By.CLASS_NAME, "button-reverse-step")
    skip_button = driver.find_element(By.CLASS_NAME, "button-skip-step")

    # Escape settings
    driver.find_element(By.TAG_NAME, "html").send_keys(Keys.ESCAPE)

    # Empty shell
    await_result(driver, "", ">>> ")

    # Run code in shell, check result
    driver.find_element(By.CSS_SELECTOR, ".terminal input").send_keys("12345\n")
    await_result(
        driver,
        "12345\n12345",
        """\
>>> 12345
12345
>>> """,
    )

    editor = driver.find_element(By.CSS_SELECTOR, "#editor textarea")
    run_button = driver.find_element(By.CSS_SELECTOR, ".editor-buttons .btn-primary")
    snoop_button = driver.find_element(By.CSS_SELECTOR, ".editor-buttons .btn-success")

    # Run test_steps within futurecoder!
    run_code(editor, run_button, get_test_steps_code())
    await_result(driver, "Introducing", (this_dir / "golden_files/en/test_transcript.json").read_text() + "\n>>> ")

    # Reverse until at first step
    for _ in range(10):
        reverse_button.click()
        if (
            "In general, you can get the element"
            not in driver.find_element(By.CSS_SELECTOR, ".book-text").text
        ):
            break
        sleep(0.1)
    else:
        pytest.fail()

    # Get code from instructions
    code = driver.find_element(By.CSS_SELECTOR, "#step-text-0 pre").text
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
        in driver.find_element(By.CSS_SELECTOR, ".book-text").text
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

    # Skip forward to output prediction step: printing_the_range
    for _ in range(3):
        skip_button.click()
        sleep(0.1)

    assert (
        "As you can see, the result is the same"
        in driver.find_element(By.CSS_SELECTOR, ".book-text").text
    )

    # Correct answer first time
    predict_output(driver, editor, run_button, 0, None)

    # start again
    reverse_button.click()

    # Correct answer second time
    predict_output(driver, editor, run_button, 1, 0)

    # start again
    reverse_button.click()

    # Two wrong answers
    predict_output(driver, editor, run_button, 1, 2)

    # Click OK
    driver.find_element(By.CSS_SELECTOR, ".submit-prediction button").click()

    # Course has moved on to next step: indices_out_of_bounds
    # Let's skip to the end of this page
    # and start on the next page with the step index_exercise
    for _ in range(6):
        skip_button.click()
        sleep(0.1)

    force_click(driver, driver.find_element(By.CLASS_NAME, "next-button"))

    assert "Given a list" in driver.find_element(By.CSS_SELECTOR, ".book-text").text

    driver.find_element(By.CSS_SELECTOR, ".assistant-hints .card-header").click()
    show_hints_and_solution(driver, num_hints=9, parsons=False)

    # Hidden solution contains correct text
    code = driver.find_element(By.CSS_SELECTOR, ".gradual-solution code")
    assert (
        code.text
        == """\
for i in range(len(things)):
    if to_find == things[i]:
        print(i)
        break"""
    )

    # Click button repeatedly to reveal solution
    get_hint_button = driver.find_element(By.CSS_SELECTOR, ".hints-popup .btn-primary")
    assert get_hint_button.text == "Reveal"
    scroll_to_bottom(driver)
    for i in range(24):
        assert len(code.find_elements(By.CLASS_NAME, "solution-token-hidden")) == 24 - i
        assert len(code.find_elements(By.CLASS_NAME, "solution-token-visible")) == 12 + i
        get_hint_button.click()

    # Open assessment
    force_click(driver, driver.find_element(By.CSS_SELECTOR, ".assistant-assessment .card-header"))

    # No messages visible
    assert not driver.find_elements(By.CLASS_NAME, "assistant-messages-message")

    # Run code which triggers a message
    run_code(editor, run_button, "12345")

    # Now we have a message
    assert (
        driver.find_element(By.CSS_SELECTOR, ".assistant-messages-message").text
        == """\
Your code should start like this:
things = '...'
to_find = '...'"""
    )

    # Run code which triggers a different message
    # Here we leave out indentation because ace adds some
    run_code(editor, run_button, """\
things = ['on', 'the', 'way', 'to', 'the', 'store']
to_find = 'the'

for i in range(len(things)):
if to_find == things[i]:
print(i)
""")

    await_result(driver, "1", "1\n4\n>>> ")

    # Now we have a message
    assert (
        driver.find_element(By.CSS_SELECTOR, ".assistant-messages-message").text
        == "You're almost there! However, this prints all the indices, not just the first one."
    )

    # Fix the solution
    editor.send_keys("        break")
    run_button.click()
    sleep(0.2)

    # Step has passed, message has disappeared
    assert not driver.find_elements(By.CLASS_NAME, "assistant-messages-message")

    # Skip to zip_longest exercise
    skip_button.click()

    # This exercise has a Parsons problem
    show_hints_and_solution(driver, num_hints=10, parsons=True)

    assert {
               node.text
               for node in driver.find_elements(By.CSS_SELECTOR, ".parsons-droppable code")
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

    # Cannot go to next page yet
    assert not driver.find_elements(By.CLASS_NAME, "next-button")

    # Next button appears after completing last step
    # Scroll to end of page to get skip button out of the way
    skip_button.click()
    sleep(0.1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(0.1)
    driver.find_element(By.CLASS_NAME, "next-button").click()

    # On next page
    sleep(0.1)
    assert (
        driver.find_element(By.CSS_SELECTOR, ".book-text h1").text
        == "Terminology: Calling functions and methods"
    )

    # Back to previous page
    driver.find_element(By.CLASS_NAME, "previous-button").click()
    sleep(0.1)
    assert driver.find_element(By.CSS_SELECTOR, ".book-text h1").text.startswith(
        "Exercises with"
    )


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def show_hints_and_solution(driver, *, num_hints, parsons):
    # Show all hints
    for hint_num in range(num_hints):
        assert len(driver.find_elements(By.CLASS_NAME, "hint-body")) == hint_num
        get_hint_button = driver.find_element(By.CSS_SELECTOR,
            ".hints-popup .btn-primary"
        )
        assert get_hint_button.text == (
            "Get a hint" if hint_num == 0 else "Get another hint"
        )
        scroll_to_bottom(driver)
        get_hint_button.click()
        if hint_num < num_hints - 1:
            hints_progress = driver.find_element(By.CSS_SELECTOR,
                ".hints-popup .hints-progress"
            )
            assert hints_progress.text == f"Shown {hint_num + 1} of {num_hints} hints"

    # All hints are shown
    assert len(driver.find_elements(By.CLASS_NAME, "hint-body")) == num_hints

    # Click 'Show solution'
    get_hint_button = driver.find_element(By.CSS_SELECTOR, ".hints-popup .btn-primary")
    assert get_hint_button.text == ("Show shuffled solution" if parsons else "Show solution")
    scroll_to_bottom(driver)
    get_hint_button.click()

    # Solution not yet visible
    assert not driver.find_elements(By.CSS_SELECTOR, ".gradual-solution")
    assert not driver.find_elements(By.CSS_SELECTOR, ".parsons-droppable")

    # Are you sure? Click 'Yes'
    get_hint_button = driver.find_element(By.CSS_SELECTOR, ".hints-popup .btn-primary")
    assert get_hint_button.text == "Yes"
    scroll_to_bottom(driver)
    get_hint_button.click()

    # Exactly one kind of solution visible
    assert bool(driver.find_elements(By.CSS_SELECTOR, ".gradual-solution")) == (not parsons)
    assert bool(driver.find_elements(By.CSS_SELECTOR, ".parsons-droppable")) == parsons


def run_code(editor, run_button, text):
    editor.send_keys(Keys.CONTROL + "a")
    editor.send_keys(Keys.BACK_SPACE)
    editor.send_keys(Keys.COMMAND + "a")
    editor.send_keys(Keys.BACK_SPACE)
    editor.send_keys(text)
    run_button.click()


def await_result(driver, part, full):
    locator = (By.CLASS_NAME, "terminal")

    WebDriverWait(driver, 20).until(text_to_be_present_in_element(locator, part))
    assert driver.find_element(*locator).text == full


def force_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def predict_output(driver, editor, run_button, first_choice, second_choice):
    is_correct = second_choice is None

    # Ensure there is no previous question still showing
    locator = (By.CLASS_NAME, "prediction-choice")
    WebDriverWait(driver, 5).until(invisibility_of_element(locator))

    # Run the verbatim code
    run_code(
        editor,
        run_button,
        """\
indices = range(4)

print(indices[0])
print(indices[1])
print(indices[2])
print(indices[3])
                """
    )

    locator = (By.CLASS_NAME, "terminal")
    WebDriverWait(driver, 5).until(text_to_be_present_in_element(locator, "This"))
    sleep(2)

    # Check the choices
    choices = driver.find_elements(By.CLASS_NAME, "prediction-choice")
    assert len(choices) == 6

    # Click first choice
    choice = choices[first_choice]
    choice.click()

    # Choice is highlighted in blue
    check_choice_status(driver, first_choice, "selected")

    # Click Submit
    driver.find_element(By.CSS_SELECTOR, ".submit-prediction button").click()
    sleep(0.1)

    check_choice_status(driver, first_choice, "correct" if is_correct else "wrong")

    if is_correct:
        bottom_text = "Correct!"
    else:
        bottom_text = "Oops, that's not right. You can try one more time!\nSubmit"
    assert driver.find_element(By.CSS_SELECTOR, ".submit-prediction").text == bottom_text

    if is_correct:
        return

    is_correct = second_choice == 0

    # Click second choice
    choice = choices[second_choice]
    force_click(driver, choice)

    # Choice is highlighted in blue
    check_choice_status(driver, first_choice, "wrong")
    check_choice_status(driver, second_choice, "selected")

    # Click Submit
    driver.find_element(By.CSS_SELECTOR, ".submit-prediction button").click()
    sleep(0.1)

    check_choice_status(driver, first_choice, "wrong")
    check_choice_status(driver, second_choice, "correct" if is_correct else "wrong")

    if is_correct:
        bottom_text = "Correct!"
    else:
        bottom_text = "Sorry, wrong answer. Try again next time!\nOK"
    assert driver.find_element(By.CSS_SELECTOR, ".submit-prediction").text == bottom_text


def check_choice_status(driver, choice_index, status):
    choices = driver.find_elements(By.CLASS_NAME, "prediction-choice")
    choice = choices[choice_index]
    assert choice.get_attribute("class") == (
        f"prediction-choice prediction-{status}"
    ), [
        choice.get_attribute("class")
        for choice in driver.find_elements(By.CLASS_NAME, "prediction-choice")
    ]


def get_test_steps_code():
    code = (this_dir / "test_steps.py").read_text()
    return f"""
# Put all code in one line to avoid ace indentation issues
exec({code!r}, globals())

os.environ['FUTURECODER_LANGUAGE'] = 'None'
os.environ['FIX_TESTS'] = '1'
test_steps()

print(open("/golden_files/None/test_transcript.json").read())
"""
