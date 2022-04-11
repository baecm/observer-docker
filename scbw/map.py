import logging
import os
import os.path
import shutil
import tempfile

from scbw.error import GameException
from scbw.utils import download_extract_zip

SC_MAP_DIR = os.path.abspath("maps")
SC_REPLAY_DIR = os.path.abspath("maps/replays")
logger = logging.getLogger(__name__)


def check_replay_exists(replay_file: str) -> None:
    if not os.path.exists(replay_file):
        raise GameException(f"Replay {replay_file} could not be found")


def download_bwta_caches(bwta_dir: str, bwta2_dir: str) -> None:
    logger.info("downloading BWTA caches")
    tmp_dir = tempfile.mkdtemp()
    download_extract_zip(
        "https://github.com/adakitesystems/DropLauncher/releases/download/0.4.18a/BWTA_cache.zip",
        tmp_dir
    )

    for file in os.listdir(tmp_dir + "/bwapi-data/BWTA"):
        if not os.path.exists(f"{bwta_dir}/{file}"):
            shutil.move(tmp_dir + "/bwapi-data/BWTA/" + file, bwta_dir)
    for file in os.listdir(tmp_dir + "/bwapi-data/BWTA2"):
        if not os.path.exists(f"{bwta_dir}/{file}"):
            shutil.move(tmp_dir + "/bwapi-data/BWTA2/" + file, bwta2_dir)
