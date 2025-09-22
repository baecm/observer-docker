import logging
import os
import os.path
import shutil
import tempfile

from observer.error import GameException


SC_MAP_DIR = os.path.abspath("maps")
logger = logging.getLogger(__name__)


def check_map_exists(map_file: str) -> None:
    if not os.path.exists(map_file):
        raise GameException(f"Map {map_file} could not be found")
