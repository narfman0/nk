from os import environ

DATA_ROOT = environ.get("NK_DATA_ROOT", "../data")
ENABLE_PROFILING = bool(environ.get("ENABLE_PROFILING", ""))
