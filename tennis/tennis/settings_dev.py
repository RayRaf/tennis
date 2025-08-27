"""
Local development settings for running with DEBUG=False but without
diagnostic debug pages and with working static files.

Usage (PowerShell):
  $env:DJANGO_SETTINGS_MODULE = "tennis.settings_dev"; python manage.py runserver
"""

from .settings import *  # noqa

# Keep production-like mode (no debug page), but enable convenient static handling.
DEBUG = False

# Make WhiteNoise serve files directly from finders without requiring collectstatic.
# This is safe for local development only.
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# Use non-manifest storage in dev so template {% static %} returns un-hashed paths
# and you don't need to run collectstatic on each change.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Keep broad hosts locally; tighten in production.
ALLOWED_HOSTS = ["*"]

# Quieter logging to avoid verbose diagnostics in console.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'WARNING',  # hide detailed runserver tracebacks
            'propagate': False,
        },
    },
}
