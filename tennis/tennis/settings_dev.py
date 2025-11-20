"""
Local development settings for running with DEBUG=False but without
diagnostic debug pages and with working static files.

Usage (PowerShell):
  $env:DJANGO_SETTINGS_MODULE = "tennis.settings_dev"; python manage.py runserver
"""

from .settings import *  # noqa

# Enable DEBUG for local development so Django serves static files automatically
DEBUG = True

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
