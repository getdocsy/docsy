import pytest
from pathlib import Path
from app.services.local_repo_service import get_documentation_file_headings


def test_get_documentation_file_headings_rst(tmp_path):
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

    # Create the test file
    test_file = tmp_path / "test.rst"
    test_file.write_text(test_content)

    # Get the headings
    headings = get_documentation_file_headings(absolute_file_path=str(test_file))

    # Verify the results
    expected_headings = ["Test Document", "Section 1", "Section 2"]
    assert headings == expected_headings
