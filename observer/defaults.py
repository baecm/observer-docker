import os
import platform


def get_data_dir() -> str:
    system = platform.system()
    if system == "Windows":
        return os.getenv('APPDATA') + "/observer"
    else:
        return os.path.expanduser("~") + "/.observer"


VERSION = "0.9.0"

OBSERVER_BASE_DIR = get_data_dir()
SC_GAME_DIR = f"{OBSERVER_BASE_DIR}/games"
SC_BWAPI_DATA_BWTA_DIR = f"{OBSERVER_BASE_DIR}/bwapi-data/BWTA"
SC_BWAPI_DATA_BWTA2_DIR = f"{OBSERVER_BASE_DIR}/bwapi-data/BWTA2"
SC_BOT_DIR = f"{OBSERVER_BASE_DIR}/bots"
SC_MAP_DIR = f"{OBSERVER_BASE_DIR}/maps"

SC_IMAGE = "starcraft:game"
SC_JAVA_IMAGE = "starcraft:java"
