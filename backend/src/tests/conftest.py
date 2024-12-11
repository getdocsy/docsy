import os
import sys
import django
from django.conf import settings

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
django.setup()

import pytest


def pytest_configure():
    print("Configuring pytest...")
    print("Django setup complete.")


# This fixture will be available to all tests
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    This fixture ensures that the database is set up for all tests.
    The `db` fixture is provided by pytest-django.
    """
    pass


# Add any other fixtures you need here
