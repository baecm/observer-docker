# Observer docker images

This repository prepares a fully working to extract/record data using BWAPI ```AIModule``` from StarCraft: Brood War game running in Wine inside of docker image.

## Installation

See [installation instructions for Windows / Linux](INSTALL.md).

It should run well on new versions of major operating systems. It was tested on:

- Microsoft Windows 10/11 (64-bit)
- Ubuntu 22.04.01, ```6.8.0-60-generic```

## Usage

### Extract Data from replay

    $ observer --extract

### Record spectating scene from replay

    $ observer --record

You can put the RealVNC client to fullscreen and play comfortably.

(Although you might want to change your screen resolution to 800x600)

The GUI is going to be probably slower than normal game due to streaming via VNC.

## Known limitations

- Headful mode needs to specify the replays manually due to "Unable to distribute map" bug.
- Headless mode not work due to `bwheadless` not designed for replay files.

## Specification
- StarCraft 1.16.1 game
- wine `2.20.0~xenial`
- base image from `sc-docker`

## Dockerhub images

Images are available on [Dockerhub](https://hub.docker.com/r/cjdahrl/starcraft/).

You can use:

    cjdahrl/starcraft:wine
    cjdahrl/starcraft:bwapi
    cjdahrl/starcraft:java
    cjdahrl/starcraft:play

These are latest stable images and are subject to change.

## About
<!-- We are pleased to publish docker images for StarCraft: Brood War and BW bots!

![Starcraft playing on Linux](resources/linux_play.png)

This means the end of complicated game setup for newcomers or people

who simply want to play StarCraft against AI bots.

You can develop your bots on your favorite platform instead of relying on Windows.

We have more things cooking: This is a part of our ongoing effort to create an easy-to-use environment for machine learning bots (bots that improve based on experience and self-play). -->

This project is maintained by [Cognition and Intelligence Lab](http://cilab.gist.ac.kr/)
