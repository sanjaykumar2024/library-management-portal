"""
Test settings — inherits everything from the main config and swaps MySQL for
SQLite so the test suite can run without a live MySQL server.
Also uses the simple static file storage to avoid manifest errors.
"""

from config.settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Use simple static files storage for tests (no manifest hashing)
STORAGES = {
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
