# -*- coding: UTF-8 -*-
from .base import *

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
    "0.0.0.0",
    "localhost",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: DEBUG}

CACHE_TTL = 10  # Set cache time to 5 seconds in dev mode

STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", default="/app/static")
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", default="/app/media")

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
