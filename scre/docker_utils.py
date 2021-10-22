import distutils.dir_util
import distutils.errors
import itertools
import logging
import os
import os.path
import re
import shutil
import subprocess
import time
from pprint import pformat
from typing import List, Optional, Callable, Dict, Any

import docker
import docker.errors
import docker.types
from scre.defaults import SCRE_BASE_DIR, SC_PARENT_IMAGE, SC_JAVA_IMAGE, SC_BINARY_LINK
from scre.error import ContainerException, DockerException, GameException, RealtimeOutedException
from scre.game_type import GameType
from scre.logs import find_frames, find_logs, find_replays, find_scores
from scre.player import BotPlayer, HumanPlayer, Player
from scre.utils import download_file, random_string
from scre.vnc import launch_vnc_viewer

logger = logging.getLogger(__name__)
# disable docker package spam logging
logging.getLogger('urllib3.connectionpool').propagate = False

docker_client = docker.from_env()

DOCKER_STARCRAFT_NETWORK = "sc_net"
SUBNET_CIDR = "172.18.0.0/16"
BASE_VNC_PORT = 5900
VNC_HOST = "localhost"
APP_DIR = "/app"
LOG_DIR = f"{APP_DIR}/logs"
SC_DIR = f"{APP_DIR}/sc"
BWTA_DIR = f"{APP_DIR}/bwta"
BWAPI_DIR = f"{APP_DIR}/bwapi"
BOT_DIR = f"{APP_DIR}/bot"
MAP_DIR = f"{SC_DIR}/maps"
ERRORS_DIR = f"{SC_DIR}/Errors"
BWAPI_DATA_DIR = f"{SC_DIR}/bwapi-data"
BWAPI_DATA_BWTA_DIR = f"{BWAPI_DATA_DIR}/BWTA"
BWAPI_DATA_BWTA2_DIR = f"{BWAPI_DATA_DIR}/BWTA2"
BOT_DATA_SAVE_DIR = f"{BWAPI_DATA_DIR}/save"
BOT_DATA_READ_DIR = f"{BWAPI_DATA_DIR}/read"
BOT_DATA_WRITE_DIR = f"{BWAPI_DATA_DIR}/write"
BOT_DATA_AI_DIR = f"{BWAPI_DATA_DIR}/AI"
BOT_DATA_LOGS_DIR = f"{BWAPI_DATA_DIR}/logs"

EXIT_CODE_REALTIME_OUTED = 2
MAX_TIME_RUNNING_SINGLE_CONTAINER = 20

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    DEVNULL = open(os.devnull, "wb")


def ensure_docker_can_run() -> None:
    """
    :raises docker.errors.ContainerError
    :raises docker.errors.ImageNotFound
    :raises docker.errors.APIError
    """
    logger.info("checking docker can run")
    version = docker_client.version()["ApiVersion"]
    docker_client.containers.run("hello-world")
    logger.debug(f"using docker API version {version}")


def ensure_local_net(
        network_name: str = DOCKER_STARCRAFT_NETWORK,
        subnet_cidr: str = SUBNET_CIDR
) -> None:
    """
    Create docker local net if not found.

    :raises docker.errors.APIError
    """
    logger.info(f"checking whether docker has network {network_name}")
    ipam_pool = docker.types.IPAMPool(subnet=subnet_cidr)
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
    networks = docker_client.networks.list(names=DOCKER_STARCRAFT_NETWORK)
    output = networks[0].short_id if networks else None
    if not output:
        logger.info("network not found, creating ...")
        output = docker_client.networks.create(DOCKER_STARCRAFT_NETWORK, ipam=ipam_config).short_id
    logger.debug(f"docker network id: {output}")


def ensure_local_image(
        local_image: str,
        parent_image: str = SC_PARENT_IMAGE,
        java_image: str = SC_JAVA_IMAGE,
        starcraft_base_dir: str = SCRE_BASE_DIR,
        starcraft_binary_link: str = SC_BINARY_LINK,
) -> None:
    """
    Check if `local_image` is present locally. If it is not, pull parent images and build.
    This includes pulling starcraft binary.

    :raises docker.errors.ImageNotFound
    :raises docker.errors.APIError
    """
    logger.info(f"checking if there is local image {local_image}")
    docker_images = docker_client.images.list(local_image)
    if len(docker_images) and docker_images[0].short_id is not None:
        logger.info(f"image {local_image} found locally.")
        return

    logger.info("image not found locally, creating...")
    pkg_docker_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "local_docker")
    base_dir = os.path.join(starcraft_base_dir, "docker")
    logger.info(f"copying files from {pkg_docker_dir} to {base_dir}.")
    distutils.dir_util.copy_tree(pkg_docker_dir, base_dir)

    starcraft_zip_file = f"{base_dir}/starcraft.zip"
    if not os.path.exists(starcraft_zip_file):
        logger.info(f"downloading starcraft.zip to {starcraft_zip_file}")
        download_file(starcraft_binary_link, starcraft_zip_file)

    logger.info(f"pulling image {parent_image}, this may take a while...")
    pulled_image = docker_client.images.pull(parent_image)
    pulled_image.tag(java_image)

    logger.info(f"building local image {local_image}, this may take a while...")
    docker_client.images.build(path=base_dir, dockerfile="game.dockerfile", tag=local_image)
    logger.info(f"successfully built image {local_image}")


def remove_game_image(image_name: str) -> None:
    try:
        docker_client.images.get(image_name)
    except docker.errors.ImageNotFound:
        pass
    except docker.errors.APIError:
        logger.error(f"there occurred an error trying to find image {image_name}")
    else:
        docker_client.images.remove(image_name, force=True)
    logger.info(f"docker image {image_name} removed.")


def check_dockermachine() -> bool:
    """
    Checks that docker-machine is available on the computer

    :raises FileNotFoundError if docker-machine is not present
    """
    logger.debug("checking docker-machine presence")
    # noinspection PyBroadException
    try:
        out = subprocess \
            .check_output(["docker-machine", "version"]) \
            .decode("utf-8") \
            .replace("docker-machine.exe", "") \
            .replace("docker-machine", "") \
            .strip()
        logger.debug(f"using docker machine version {out}")
        return True
    except Exception:
        logger.debug(f"docker machine not present")
        return False


def dockermachine_ip() -> Optional[str]:
    """
    Gets IP address of the default docker machine
    Returns None if no docker-machine executable
    in the PATH and if there no Docker machine
    with name default present
    """
    if not check_dockermachine():
        return None

    # noinspection PyBroadException
    try:
        out = subprocess.check_output(['docker-machine', 'ip'])
        return out.decode("utf-8").strip()
    except Exception:
        logger.debug(f"docker machine not present")
        return None


def xoscmounts(host_mount):
    """
    Cross OS compatible mount dirs
    """
    callback_lower_drive_letter = lambda pat: pat.group(1).lower()
    host_mount = re.sub(r"^([a-zA-Z])\:", callback_lower_drive_letter, host_mount)
    host_mount = re.sub(r"^([a-z])", "//\\1", host_mount)
    host_mount = re.sub(r"\\", "/", host_mount)
    return host_mount


def launch_image(
        # players info
        player: Player,

        # game settings
        headless: bool,
        game_name: str,
        replay_name: str,
        game_speed: int,
        allow_input: bool,

        # mount dirs
        game_dir: str,
        bot_dir: str,
        map_dir: str,
        bwapi_data_bwta_dir: str,
        bwapi_data_bwta2_dir: str,

        vnc_base_port: int,
        vnc_host: int,
        capture_movement: bool,

        # docker
        docker_image: str,
        docker_opts: List[str]
) -> None:
    """
    :raises docker,errors.APIError
    :raises DockerException
    """
    container_name = f"{game_name}_{player.name.replace(' ', '_')}"

    log_dir = f"{game_dir}/{game_name}/logs"
    crashes_dir = f"{game_dir}/{game_name}/crashes"
    os.makedirs(log_dir, mode=0o777, exist_ok=True)  # todo: proper mode
    os.makedirs(crashes_dir, mode=0o777, exist_ok=True)  # todo: proper mode

    volumes = {
        xoscmounts(log_dir): {"bind": LOG_DIR, "mode": "rw"},
        xoscmounts(map_dir): {"bind": MAP_DIR, "mode": "rw"},
        xoscmounts(crashes_dir): {"bind": ERRORS_DIR, "mode": "rw"},
        xoscmounts(bwapi_data_bwta_dir): {"bind": BWAPI_DATA_BWTA_DIR, "mode": "rw"},
        xoscmounts(bwapi_data_bwta2_dir): {"bind": BWAPI_DATA_BWTA2_DIR, "mode": "rw"},
    }

    ports = {}
    if not headless:
        ports.update({"5900/tcp": vnc_base_port})

    env = dict(
        PLAYER_NAME=player.name,
        GAME_NAME=game_name,
        REPLAY_NAME=f"/app/sc/maps/replays/{replay_name}",
        SPEED_OVERRIDE=game_speed,

        TM_LOG_RESULTS=f"../logs/scores.json",
        TM_LOG_FRAMETIMES=f"../logs/frames.csv",
        TM_SPEED_OVERRIDE=game_speed,
        TM_ALLOW_USER_INPUT="1" if isinstance(player, HumanPlayer) or allow_input else "0",

        EXIT_CODE_REALTIME_OUTED=EXIT_CODE_REALTIME_OUTED,
        CAPTURE_MOUSE_MOVEMENT="1" if capture_movement else "0",

        JAVA_DEBUG="0"
    )

    if isinstance(player, BotPlayer):
        # Only mount write directory, read and AI
        # are copied from the bot directory in proper places in bwapi-data
        bot_data_write_dir = f"{game_dir}/{game_name}/write/"
        os.makedirs(bot_data_write_dir, mode=0o777, exist_ok=True)  # todo: proper mode
        volumes.update({
            xoscmounts(bot_data_write_dir): {"bind": BOT_DATA_WRITE_DIR, "mode": "rw"},
            xoscmounts(player.bot_dir): {"bind": BOT_DIR, "mode": "ro"},
        })
        env["BOT_FILE"] = player.bot_basefilename
        env["BOT_BWAPI"] = player.bwapi_version

        env["JAVA_DEBUG"] = "0"
        env["JAVA_DEBUG_PORT"] = ""
        env["JAVA_OPTS"] = ""

        command = ["/app/play_bot.sh"]
        if player.meta.javaDebugPort is not None:
            ports.update({"player.meta.javaDebugPort/tcp": player.meta.javaDebugPort})
            env["JAVA_DEBUG"] = "1"
            env["JAVA_DEBUG_PORT"] = player.meta.javaDebugPort
        if player.meta.javaOpts is not None:
            env["JAVA_OPTS"] = player.meta.javaOpts
        if player.meta.port is not None:
            if isinstance(player.meta.port, int) or player.meta.port.isdigit():
                ports.update({str(player.meta.port) + '/tcp': int(player.meta.port)})
            else:
                forward, local = [int(x) for x in player.meta.port.split(':')]
                ports.update({str(local) + '/tcp': forward})
    else:
        pass

    entrypoint_opts = ["--headful"]
    if headless:
        entrypoint_opts = [
            "--game", game_name, "--name", player.name,
        ]
        entrypoint_opts += ["--host", "--map", f"/app/sc/maps/replays/{replay_name}"]
    command += entrypoint_opts

    logger.debug(
        "\n"
        f"docker_image={docker_image}\n"
        f"command={pformat(command, indent=4)}\n"
        f"name={container_name}\n"
        f"detach={True}\n"
        f"environment={pformat(env, indent=4)}\n"
        f"privileged={True}\n"
        f"volumes={pformat(volumes, indent=4)}\n"
        f"network={DOCKER_STARCRAFT_NETWORK}\n"
        f"ports={ports}\n"
    )

    container = docker_client.containers.run(
        docker_image,
        command=command,
        name=container_name,
        detach=True,
        environment=env,
        privileged=True,
        volumes=volumes,
        network=DOCKER_STARCRAFT_NETWORK,
        ports=ports
    )
    if container:
        container_id = running_containers(container_name)
        logger.info(f"launched {player}")
        logger.debug(f"container name = '{container_name}', container id = '{container_id}'")
    else:
        raise DockerException(f"could not launch {player} in container {container_name}")


def running_containers(name_filter: str) -> List[str]:
    """
    :raises docker.exceptions.APIError
    """
    return [container.short_id for container in
            docker_client.containers.list(filters={"name": name_filter})]


def remove_game_containers(name_filter: str) -> None:
    """
    :raises docker.exceptions.APIError
    """
    for container in docker_client.containers.list(filters={"name": name_filter}, all=True):
        container.stop()
        container.remove()


def container_exit_code(container_id: str) -> Optional[int]:
    """
    :raises docker.errors.NotFound
    :raises docker.errors.APIError
    """
    container = docker_client.containers.get(container_id)
    return container.wait()["StatusCode"]


def launch_game(
        player: Player,
        launch_params: Dict[str, Any],
        show_all: bool,
        read_overwrite: bool,
        wait_callback: Callable
) -> None:
    """
    :raises DockerException, ContainerException, RealtimeOutedException
    """
    if not player:
        raise GameException("at least one player must be specified")

    game_dir = launch_params["game_dir"]
    game_name = launch_params["game_name"]

    if os.path.exists(f"{game_dir}/{game_name}"):
        logger.info(f"removing existing game results of {game_name}")
        shutil.rmtree(f"{game_dir}/{game_name}")

    launch_image(player, **launch_params)

    logger.debug("checking if game has launched properly...")
    time.sleep(1)
    start_containers = running_containers(game_name + "_")

    if not launch_params["headless"]:
        port = launch_params["vnc_base_port"]
        host = launch_params["vnc_host"]
        logger.info(f"launching vnc viewer for {player} on address {host}:{port}")
        launch_vnc_viewer(host, port)

        logger.info("\n"
                    "In headful mode, you must specify and start the game manually.\n"
                    "Select the map, wait for bots to join the game "
                    "and then start the game.")

    logger.info(f"waiting until game {game_name} is finished...")
    running_time = time.time()
    while True:
        containers = running_containers(game_name)
        # if len(containers) == 0:  # game finished
        #     break
        # if len(containers) >= 2:  # update the last time when there were multiple containers
        #     running_time = time.time()
        # if len(containers) == 1 and time.time() - running_time > MAX_TIME_RUNNING_SINGLE_CONTAINER:
        #     raise ContainerException(
        #         f"One lingering container has been found after single container "
        #         f"timeout ({MAX_TIME_RUNNING_SINGLE_CONTAINER} sec), the game probably crashed.")
        logger.debug(f"waiting. {containers}")
        wait_callback()

    exit_codes = [container_exit_code(container) for container in containers]

    # remove containers before throwing exception
    logger.debug("removing game containers")
    remove_game_containers(game_name)

    if any(exit_code == EXIT_CODE_REALTIME_OUTED for exit_code in exit_codes):
        raise RealtimeOutedException(f"some of the game containers has realtime outed.")
    if any(exit_code == 1 for exit_code in exit_codes):
        raise ContainerException(f"some of the game containers has finished with error exit code.")

    if read_overwrite:
        logger.info("overwriting bot files")
        if isinstance(player, BotPlayer):
            logger.debug(f"overwriting files for {player}")
            distutils.dir_util.copy_tree(
                f"{game_dir}/{game_name}/write",
                player.read_dir
            )
