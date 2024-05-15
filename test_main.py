import unittest
import os
import tempfile
from unittest.mock import patch, mock_open, Mock
from main import search_untitled_files, generate_title
import json


class TestMain(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_search_untitled_files(self):
        # Create some test files
        open(os.path.join(self.test_dir.name, "Untitled.md"), "w").close()
        open(os.path.join(self.test_dir.name, "Untitled 1.md"), "w").close()
        open(os.path.join(self.test_dir.name, "無題のファイル.md"), "w").close()
        open(os.path.join(self.test_dir.name, "OtherFile.md"), "w").close()

        # Call the function
        result = search_untitled_files(self.test_dir.name)

        # Check the result
        expected = [
            os.path.join(self.test_dir.name, "Untitled.md"),
            os.path.join(self.test_dir.name, "Untitled 1.md"),
            os.path.join(self.test_dir.name, "無題のファイル.md"),
        ]
        self.assertCountEqual(result, expected)

    @patch("main.completion")
    def test_generate_title(self, mock_completion):
        # Mock the response from the completion function
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function = Mock()
        mock_response.choices[0].message.tool_calls[0].function.arguments = json.dumps(
            {"title": "TestTitle"}
        )
        mock_completion.return_value = mock_response

        # Use a mock file content
        file_content = "# Sample Markdown Content"
        mock_open_obj = mock_open(read_data=file_content)

        with patch("builtins.open", mock_open_obj):
            result = generate_title("/path/to/mock/file.md")

        self.assertEqual(result, "TestTitle")


if __name__ == "__main__":
    unittest.main()
