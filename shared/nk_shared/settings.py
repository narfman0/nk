from os import environ

PROJECT_ROOT = environ.get("NK_PROJECT_ROOT", "..")
DATA_ROOT = environ.get("NK_DATA_ROOT", f"{PROJECT_ROOT}/data")
ENABLE_PROFILING = bool(environ.get("ENABLE_PROFILING", ""))
MAP_WIDTH = 1000
