import pytest
from django.conf import settings

@pytest.mark.django_db
def test_settings():
    assert settings.SECRET_KEY == 'django-insecure-test-key' 