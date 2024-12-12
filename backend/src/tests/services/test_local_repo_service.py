import unittest
import tempfile
import os
from app.services.local_repo_service import get_documentation_file_headings


class TestLocalRepoService(unittest.TestCase):
    def test_get_documentation_file_headings_rst(self):
        # Create a temporary RST file with some test content
        test_content = """
Test Document
============

Section 1
---------

Some content here.

Section 2
---------

More content here.
"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".rst", delete=False
        ) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Get the headings
            headings = get_documentation_file_headings(
                absolute_file_path=temp_file_path
            )

            # Verify the results
            expected_headings = ["Test Document", "Section 1", "Section 2"]
            self.assertEqual(headings, expected_headings)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
