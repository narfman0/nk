from os import environ

from dotenv import load_dotenv

load_dotenv()

WIDTH = int(environ.get("WIDTH", "1920"))
HEIGHT = int(environ.get("HEIGHT", "1080"))
FPS = int(environ.get("FPS", "60"))
NK_DATA_ROOT = environ.get("NK_DATA_ROOT", "../data")
