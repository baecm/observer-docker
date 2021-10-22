import os
import platform


def get_data_dir() -> str:
    system = platform.system()
    if system == "Windows":
        return os.getenv('APPDATA') + "/scre"
    else:
        return os.path.expanduser("~") + "/.scre"


VERSION = "1.0.4"

SCRE_BASE_DIR = get_data_dir()
SC_GAME_DIR = f"{SCRE_BASE_DIR}/games"
SC_BWAPI_DATA_BWTA_DIR = f"{SCRE_BASE_DIR}/bwapi-data/BWTA"
SC_BWAPI_DATA_BWTA2_DIR = f"{SCRE_BASE_DIR}/bwapi-data/BWTA2"
SC_BOT_DIR = f"{SCRE_BASE_DIR}/bots"
SC_MAP_DIR = f"{SCRE_BASE_DIR}/maps"

SC_IMAGE = "starcraft:game-" + VERSION
SC_PARENT_IMAGE = "ggaic/starcraft:java-" + VERSION
SC_JAVA_IMAGE = "starcraft:java"
SC_BINARY_LINK = "http://files.theabyss.ru/sc/starcraft.zip"
