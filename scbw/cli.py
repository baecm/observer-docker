import argparse
import logging
import os.path
import sys

import coloredlogs
import docker
from scbw.defaults import (
    SC_BOT_DIR, SC_GAME_DIR, SC_MAP_DIR, SCBW_BASE_DIR, SC_IMAGE,
    SC_BWAPI_DATA_BWTA_DIR, SC_BWAPI_DATA_BWTA2_DIR, VERSION
)
from scbw.docker_utils import BASE_VNC_PORT, VNC_HOST
from scbw.error import ScreException
from scbw.game import run_game
from scbw.player import bot_regex
from scbw.utils import random_string

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description='Launch StarCraft docker images for bot/human headless/headful play',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--install', action='store_true',
                    help="Download all dependencies and data files.\n"
                         "Needed to run the first time after `pip install`.")

parser.add_argument('--bot', type=bot_regex,
                    metavar="BOT_NAME",
                    help='Specify the names of the bot that should play.\n'
                         'The bot is looked up in the --bot_dir directory.\n'
                         '  --bot REPLAY_EXTRACTOR')
parser.add_argument('--replay', type=str, metavar="REPLAY.rep",
                    default="1-2-3-UAI12.rep",
                    help="Name of replay on which SC should be played,\n"
                         "relative to --replay_dir")
parser.add_argument('--headless', action='store_true',
                    help="Launch play in headless mode. \n"
                         "No VNC viewer will be launched.")
# Game settings
parser.add_argument("--game_name", type=str, default=random_string(8),
                    help="Override the auto-generated game name")
parser.add_argument("--game_speed", type=int, default=0,
                    help="Set game speed (pause of ms between frames),\n"
                         "use -1 for game default.")
# Volumes
parser.add_argument('--bot_dir', type=str, default=SC_BOT_DIR,
                    help=f"Directory where bots are stored, default:\n{SC_BOT_DIR}")
parser.add_argument('--game_dir', type=str, default=SC_GAME_DIR,
                    help=f"Directory where game logs and results are stored, default:\n{SC_GAME_DIR}")
parser.add_argument('--map_dir', type=str, default=SC_MAP_DIR,
                    help=f"Directory where maps are stored, default:\n{SC_MAP_DIR}")
#  BWAPI data volumes
parser.add_argument('--bwapi_data_bwta_dir', type=str, default=SC_BWAPI_DATA_BWTA_DIR,
                    help=f"Directory where BWTA map caches are stored, "
                         f"default:\n{SC_BWAPI_DATA_BWTA_DIR}")
parser.add_argument('--bwapi_data_bwta2_dir', type=str, default=SC_BWAPI_DATA_BWTA2_DIR,
                    help=f"Directory where BWTA2 map caches are stored, "
                         f"default:\n{SC_BWAPI_DATA_BWTA2_DIR}")
# VNC
parser.add_argument('--vnc_base_port', type=int, default=BASE_VNC_PORT,
                    help="VNC lowest port number (for server).\n"
                         "Each consecutive n-th client (player)\n"
                         "has higher port number - vnc_base_port+n ")
parser.add_argument('--vnc_host', type=str, default='',
                    help="Address of the host on which VNC connections would be accessible\n"
                         f"default:\n{VNC_HOST} or IP address of the docker-machine")
parser.add_argument('--capture_movement', action="store_true",
                    help="If mouse gets outside of the VNC window, \n"
                         "do not move the game (only use mini map)")
# Settings
parser.add_argument('--show_all', action="store_true",
                    help="Launch VNC viewers for all containers, not just the server.")
parser.add_argument('--allow_input', action="store_true",
                    help="Allow controlling the game for running bots. Useful for debugging.")
parser.add_argument('--log_level', type=str, default="INFO",
                    choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                    help="Logging level.")
parser.add_argument('--log_verbose', action="store_true",
                    help="Add more information to logging, as time and PID.")
parser.add_argument('--read_overwrite', action="store_true",
                    help="At the end of each game, copy the contents\n"
                         "of 'write' directory to the read directory\n"
                         "of the bot.\n"
                         "Needs to be explicitly turned on.")
parser.add_argument('--docker_image', type=str, default=SC_IMAGE,
                    help="The name of the image that should \n"
                         "be used to launch the game.\n"
                         "This helps with local development.")
parser.add_argument('--opt', type=str,
                    help="Specify custom docker run options")
parser.add_argument('--plot_realtime', action='store_true',
                    help="Allow realtime plotting of frame information.\n"
                         "At the end of the game, this plot will be saved\n"
                         "to file {GAME_DIR}/{GAME_NAME}/frame_plot.png")
parser.add_argument('-v', "--version", action='store_true', dest='show_version',
                    help="Show current version")


def _image_version_up_to_date():
    client = docker.from_env()
    return any(tag == SC_IMAGE for image in client.images.list('starcraft-cog') for tag in image.tags)


# todo: add support for multi-PC play.
# We need to think about how to setup docker IPs,
# maybe we will need to specify manually routing tables? :/

def main():
    args = parser.parse_args()
    if args.show_version:
        print(VERSION)
        sys.exit(0)

    coloredlogs.install(
        level=args.log_level,
        fmt="%(asctime)s %(levelname)s %(name)s[%(process)d] %(message)s" if args.log_verbose
        else "%(levelname)s %(message)s")

    if args.install or not _image_version_up_to_date():
        from .install import install
        try:
            install()
            if args.install:
                sys.exit(0)
        except ScreException as e:
            logger.exception(e)
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)

    if not os.path.exists(SCBW_BASE_DIR):
        parser.error(f'The data directory {SCBW_BASE_DIR} was not found. '
                     f'Did you run "scbw.play --install"?')
        # parser.error exits

    # bots are always required, but not if showing version :)
    if not args.bot:
        parser.error('the following arguments are required: --bot')
        # parser.error exits

    if os.path.exists(f"{args.game_dir}/GAME_{args.game_name}"):
        logger.info(f'Game {args.game_name} has already been played, '
                    f'do you wish to continue (and remove logs) ? (Y/n)')
        answer = input()
        if answer.lower() not in ("", "yes", "y"):
            sys.exit(1)

    try:
        game_result = run_game(args)
        if game_result is None:
            logger.info("Game results are available only for 1v1 (bot vs bot) games.")
            sys.exit(0)

        logger.info(f"Game {game_result.game_name} "
                    f"finished in {game_result.game_time:.2f} seconds.")
        logger.info("---")
        logger.info("Logs are saved here:")
        for log_file in sorted(game_result.log_files):
            logger.info(log_file)
        logger.info("---")

        logger.info("Frame information is saved here:")
        for frame_file in sorted(game_result.frame_files):
            logger.info(frame_file)
        logger.info("---")

        logger.info("Game results are saved here:")
        for frame_file in sorted(game_result.score_files):
            logger.info(frame_file)
        logger.info("---")

        if game_result.is_realtime_outed:
            logger.error("Game has realtime outed!")
            sys.exit(1)
        if game_result.is_gametime_outed:
            logger.error("Game has gametime outed!")
            sys.exit(1)
        if game_result.is_crashed:
            logger.error("Game has crashed!")
            sys.exit(1)

    except ScreException as e:
        logger.exception(e)
        sys.exit(1)

    except KeyboardInterrupt:
        sys.exit(1)
