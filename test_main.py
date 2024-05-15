import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, mock_open, patch

from main import generate_title, main, search_untitled_files


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

    @patch("main.completion")
    def test_generate_title_no_tool_calls(self, mock_completion):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.tool_calls = []

        mock_completion.return_value = mock_response

        file_content = "# Sample Markdown Content"
        mock_open_obj = mock_open(read_data=file_content)

        with patch("builtins.open", mock_open_obj), patch("builtins.print"):
            with self.assertRaises(Exception) as context:
                generate_title("/path/to/mock/file.md")

        self.assertTrue("All attempts failed." in str(context.exception))

    @patch("main.os")
    @patch("main.generate_title")
    @patch("main.search_untitled_files")
    def test_main(self, mock_search_untitled_files, mock_generate_title, mock_os):
        mock_search_untitled_files.return_value = ["file1.md", "file2.md"]
        mock_generate_title.return_value = "GeneratedTitle"
        mock_os.path.getsize.side_effect = [
            100,  # file1.md is 100 byte
            0,  # file2.md is 0 byte
        ]
        mock_os.path.exists.return_value = False
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.dirname.side_effect = lambda p: "mock_dir"

        with patch("sys.argv", ["main.py", self.test_dir.name]), patch(
            "builtins.print"
        ):
            main(sys.argv)

        mock_search_untitled_files.assert_called_once_with(self.test_dir.name)
        mock_generate_title.assert_called_once_with("file1.md")
        mock_os.remove.assert_called_once_with("file2.md")
        mock_os.rename.assert_called_once_with("file1.md", "mock_dir/GeneratedTitle.md")

    def test_main_no_arguments(self):
        with patch("sys.argv", ["main.py"]), patch("builtins.print") as mock_print:
            with self.assertRaises(SystemExit) as cm:
                main(sys.argv)
            mock_print.assert_called_once_with("Usage: python main.py <directory>")
            self.assertEqual(cm.exception.code, 1)

    @patch("main.os")
    @patch("main.generate_title")
    @patch("main.search_untitled_files")
    def test_main_rename_file_exists(
        self, mock_search_untitled_files, mock_generate_title, mock_os
    ):
        mock_search_untitled_files.return_value = ["file1.md"]
        mock_generate_title.return_value = "GeneratedTitle"
        mock_os.path.getsize.return_value = 100
        mock_os.path.exists.side_effect = lambda p: p == "mock_dir/GeneratedTitle.md"
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.dirname.side_effect = lambda p: "mock_dir"

        with patch("sys.argv", ["main.py", self.test_dir.name]), patch(
            "builtins.print"
        ) as mock_print:
            main(sys.argv)

        mock_search_untitled_files.assert_called_once_with(self.test_dir.name)
        mock_generate_title.assert_called_once_with("file1.md")
        mock_os.rename.assert_not_called()
        mock_print.assert_any_call(
            "File mock_dir/GeneratedTitle.md already exists. Skipping."
        )


if __name__ == "__main__":
    unittest.main()
