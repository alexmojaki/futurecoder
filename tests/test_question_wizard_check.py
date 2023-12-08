import unittest
from core.question_wizard import question_wizard_check


class TestQuestionWizardCheck(unittest.TestCase):
    def test_question_wizard_check_matching(self):
        # Example test data
        entry = {
            "source": "editor",
            "input": "print('Hello, World!')",
            "expected_output": "Hello, World!\n",
            "page_slug": "example",
            "step_name": "example_step",
            "question_wizard": True,
        }
        output = "Hello, World!\n"

        # Create a simple runner instance (you might need to adjust this based on your needs)
        class SimpleRunner:
            def __init__(self):
                self.input_nodes = {}

        runner = SimpleRunner()

        # Call the function under test
        formatted_messages, status = question_wizard_check(entry, output, runner)

        # Check the status
        self.assertEqual(status, "messages", "Status should be 'messages'")

        # Add more specific assertions based on your expected behavior
        self.assertTrue(formatted_messages, "Formatted messages should not be empty")


if __name__ == "__main__":
    unittest.main()
