<!-- observer-docker/README.md -->
# Observer docker images

This repository prepares a fully working to extract/record data using BWAPI ```AIModule``` from StarCraft: Brood War game running in Wine inside of docker image.

## Installation

See [installation instructions for Windows / Linux](INSTALL.md).

It should run well on new versions of major operating systems. It was tested on:

- Microsoft Windows 10/11 (64-bit)
- Ubuntu 22.04.01, ```6.8.0-60-generic```

## Usage

### Extract Data from replay
```bash
# On Windows, the default directory is %APPDATA%\observer\.
# On Linux, it is ~/.observer/.
# If the directory is empty, copy the ./bots folder (Extractor and Recorder) into it.
observer --extract [--replay <REPLAY.rep>] [--bot-dir <BOT_DIRECTORY>] [--game-dir <GAME_OUTPUT_DIRECTORY>]
```
### Record spectating scene from replay
```bash
observer --record [--replay <REPLAY.rep>] [--bot_dir <BOT_DIRECTORY>]
```

`--replay` copies the replay to `<map_dir>/replays/input/` and BWAPI opens it on start (single player auto menu), so no manual selection is needed. Without it, select the replay inside the container.

### Watch a replay with preset cameras
```bash
# DIR holds top<k>/<replay file>.vpd camera tracks (starcraft-vision scripts/demo_vpd.py)
observer --replay <REPLAY.rep> --tracks <DIR> [--viewers 1-3] [--labels ...]
# or name the tracks yourself
observer --replay <REPLAY.rep> --preset <TRACK1.vpd> [<TRACK2.vpd> ...]
```
Each viewer is a container running the PresetObserver bot, which moves its camera along its track and shows its label ("Camera n") top left; a VNC viewer opens per container (ports 5900, 5901, ...). One viewer plays the replay alone; several watch it together in one LAN game: the first hosts, the others join, and the host clicks Start after they have had time to join (`REPLAY_START_DELAY`). A replay lobby takes at most as many viewers as the replay has players (2 for a 1v1), so `--viewers` defaults to that number, capped at 3, and more is refused.
You can put the RealVNC client to fullscreen and play comfortably.

(Although you might want to change your screen resolution to 800x600)

The GUI is going to be probably slower than normal game due to streaming via VNC.

**Without `--replay`, both observer --extract and observer --record require manual replay selection inside the container after launch.**

## Known limitations 

- Headful mode needs to specify the replays manually due to "Unable to distribute map" bug, unless `--replay` is given.
- Headless mode not work due to `bwheadless` not designed for replay files.

## Specification
- StarCraft 1.16.1 game
- wine `2.20.0~xenial`
- base image from `sc-docker`

## Dockerhub images

Images are available on [Dockerhub](https://hub.docker.com/r/cjdahrl/starcraft/).

You can use:
```
cjdahrl/starcraft:wine
cjdahrl/starcraft:bwapi
cjdahrl/starcraft:java
cjdahrl/starcraft:play
```
These are latest stable images and are subject to change.

## About
This project is maintained by [Cognition and Intelligence Lab](http://cilab.gist.ac.kr/)
