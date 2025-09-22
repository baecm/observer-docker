import logging
import os
import os.path

from observer.defaults import (
    OBSERVER_BASE_DIR, SC_IMAGE, SC_GAME_DIR, SC_BOT_DIR, SC_MAP_DIR
)
from observer.docker_utils import (
    ensure_docker_can_run, ensure_local_net,
    check_for_game_image
)
from observer.utils import create_data_dirs

logger = logging.getLogger(__name__)


def install() -> None:
    if os.path.exists(OBSERVER_BASE_DIR):
        logger.warning(f"Path {OBSERVER_BASE_DIR} found, re-installing observer package.")
        logger.warning("Re-creating the base game image...")

    ensure_docker_can_run()
    ensure_local_net()

    # ensure docker image is present
    check_for_game_image(SC_IMAGE)

    create_data_dirs(
        SC_GAME_DIR,
        SC_BOT_DIR,
        SC_MAP_DIR,
    )

    os.makedirs(f"{SC_MAP_DIR}/replays", exist_ok=True)
    os.makedirs(f"{SC_MAP_DIR}/BroodWar", exist_ok=True)

    logger.info("Install finished. Data files are located in")
    logger.info(OBSERVER_BASE_DIR)


if __name__ == '__main__':
    install()
