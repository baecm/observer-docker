import enum
import glob
import json
import logging
import os
import signal
import time
from argparse import Namespace
from typing import List, Optional, Callable

from scre.bot_factory import retrieve_bot
from scre.bot_storage import LocalBotStorage
from scre.docker_utils import (
    dockermachine_ip, launch_game,
    remove_game_containers
)
from scre.error import GameException, RealtimeOutedException
from scre.game_type import GameType
from scre.player import HumanPlayer, BotPlayer
from scre.plot import RealtimeFramePlotter
from scre.result import GameResult
from scre.vnc import check_vnc_exists

logger = logging.getLogger(__name__)


class GameArgs(Namespace):
    bots: List[str]
    human: bool
    map: str
    headless: bool
    game_name: str
    game_type: str
    game_speed: int
    hide_names: bool
    random_names: bool
    timeout: int
    bot_dir: str
    game_dir: str
    map_dir: str
    bwapi_data_bwta_dir: str
    bwapi_data_bwta2_dir: str
    vnc_base_port: int
    vnc_host: str
    capture_movement: bool
    auto_launch: bool
    show_all: bool
    allow_input: bool
    plot_realtime: bool
    read_overwrite: bool
    docker_image: str
    opt: str


def run_game(
        args: GameArgs,
        wait_callback: Optional[Callable] = None
) -> Optional[GameResult]:
    # Check all startup requirements
    if not args.headless:
        check_vnc_exists()
    if args.headless and args.show_all:
        raise GameException("Cannot show all screens in headless mode")

    # Each game is prefixed with "GAME_"
    # this is needed for game filtering in docker ps
    game_name = "GAME_" + args.game_name

    # Prepare players
    if args.bot is None:
        args.bot = []

    bot_storages = (
        LocalBotStorage(args.bot_dir),
    )
    player = retrieve_bot(args.bots, bot_storages)

    opts = [] if not args.opt else args.opt.split(" ")

    if args.vnc_host == "":
        args.vnc_host = dockermachine_ip() or "localhost"
        logger.debug(f"Using vnc host '{args.vnc_host}'")

    # make sure we always have a sleeping wait callback!
    if wait_callback is None:
        wait_callback = lambda: time.sleep(3)

    if args.plot_realtime:
        plot_realtime = RealtimeFramePlotter(args.game_dir, game_name, player)

        def _wait_callback():
            plot_realtime.redraw()
            wait_callback()
    else:
        _wait_callback = wait_callback

    # Prepare game launching
    launch_params = dict(
        # game settings
        headless=args.headless,
        game_name=game_name,
        map_name=args.map,
        game_speed=args.game_speed,
        timeout=args.timeout,
        allow_input=args.allow_input,
        auto_launch=args.auto_launch,
        random_names=args.random_names,

        # mount dirs
        game_dir=args.game_dir,
        bot_dir=args.bot_dir,
        map_dir=args.map_dir,
        bwapi_data_bwta_dir=args.bwapi_data_bwta_dir,
        bwapi_data_bwta2_dir=args.bwapi_data_bwta2_dir,

        # vnc
        vnc_base_port=args.vnc_base_port,
        vnc_host=args.vnc_host,
        capture_movement=args.capture_movement,

        # docker
        docker_image=args.docker_image,
        docker_opts=opts,
    )

    time_start = time.time()
    is_realtime_outed = False
    try:
        launch_game(
            player, launch_params, args.show_all,
            args.read_overwrite, _wait_callback
        )
    except RealtimeOutedException:
        is_realtime_outed = True

    except KeyboardInterrupt:
        logger.warning("Caught interrupt, shutting down containers")
        logger.warning("This can take a moment, please wait.")

        # prevent another throw of KeyboardInterrupt exception
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        remove_game_containers(game_name)
        logger.info(f"Game cancelled.")
        raise

    if args.plot_realtime:
        plot_realtime.save(f"{args.game_dir}/{game_name}/frame_plot.png")

    if is_1v1_game:
        game_time = time.time() - time_start
        game_result = GameResult(
            game_name, players, game_time,
            # game error states
            is_realtime_outed,
            # dirs with results
            args.map_dir, args.game_dir
        )

        info = launch_params.copy()
        info.update(dict(
            read_overwrite=args.read_overwrite,
            bots=args.bots,

            is_crashed=game_result.is_crashed,
            is_gametime_outed=game_result.is_gametime_outed,
            is_realtime_outed=game_result.is_realtime_outed,
            game_time=game_result.game_time,

            winner=None,
            loser=None,
            winner_race=None,
            loser_race=None,
        ))
        if game_result.is_valid:
            info.update(dict(
                winner=game_result.winner_player.name,
                loser=game_result.loser_player.name,
                winner_race=game_result.winner_player.race.value,
                loser_race=game_result.loser_player.race.value,
            ))

        logger.debug(info)
        with open(f"{args.game_dir}/{game_name}/result.json", "w") as f:
            json.dump(info, f, cls=EnumEncoder)
        logger.info(f"game {game_name} recorded")

        return game_result

    return None


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return super(EnumEncoder, self).default(obj)
