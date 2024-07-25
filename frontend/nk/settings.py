from os import environ

WIDTH = int(environ.get("WIDTH", "1920"))
HEIGHT = int(environ.get("HEIGHT", "1080"))
FPS = int(environ.get("FPS", "60"))
ENABLE_PROFILING = bool(environ.get("ENABLE_PROFILING", ""))
