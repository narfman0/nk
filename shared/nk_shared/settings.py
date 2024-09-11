from os import environ
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = environ.get("NK_PROJECT_ROOT", "..")
DATA_ROOT = environ.get("NK_DATA_ROOT", f"{PROJECT_ROOT}/data")
ENABLE_PROFILING = bool(environ.get("ENABLE_PROFILING", ""))
MAPGEN_WIDTH = int(environ.get("MAPGEN_WIDTH", "200"))
ZONE_NAME = environ.get("ZONE_NAME", "1")
