import os
import pytest
import tempfile
from textwrap import dedent
import django
from django.conf import settings

from .vale import ValeFileAnalysis, analyze_file_vale, setup_vale_ini_file


def pytest_configure():
    settings.configure(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        INSTALLED_APPS=[
            "app",  # Add your app name here
        ],
    )
    django.setup()


@pytest.fixture
def vale_ini_path():
    return setup_vale_ini_file()


@pytest.fixture
def test_markdown_file():
    # Create a temporary markdown file with some content that will trigger Vale warnings
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            dedent(
                """
            # Test Document

            This is very good. You should definitely use passive voice here.
            
            Things are being done in a way that is not optimal.
        """
            )
        )
        temp_path = f.name

    yield temp_path

    # Cleanup after test
    os.unlink(temp_path)


@pytest.mark.asyncio
async def test_analyze_file_vale(vale_ini_path, test_markdown_file):
    # Run the analysis
    result = await analyze_file_vale(
        absolute_file_path=test_markdown_file,
        vale_ini_file_path=vale_ini_path,
        local_repo_path=os.path.dirname(test_markdown_file),
    )

    print(result)

    # Verify the result structure
    assert isinstance(result, ValeFileAnalysis)
