from os import environ

DATA_ROOT = environ.get("NK_DATA_ROOT", "../data")
SENTRY_DSN = environ.get("SENTRY_DSN", "")
