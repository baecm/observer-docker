# Install

<!-- What works (has been tested): -->

  <!-- - _Linux_: headful/headless play, 1v1 (bot, human), VNC -->
  <!-- - Bot type: `AI_MODULE`, `EXE`, `JAVA_JNI`, `JAVA_MIRROR` -->
  <!-- - [Tested on all SSCAIT 2017 tournament bots (and works on most)](tested_bots.md) -->


Table of contents:

  <!-- * [Ubuntu](#ubuntu) -->
  * [Windows](#windows)
  <!-- * [Mac](#mac) -->

Docker version used to build the images is `27.3.1, build ce12230`

Currently supports only `Python >= 3.6`

## Windows

### Docker

You may want to [read through manual for installing docker on Windows](https://docs.docker.com/docker-for-windows/install/)
for troubleshooting.

- Go to [docker releases for Windows](https://docs.docker.com/desktop/release-notes/)
  and download `Docker Desktop Installer 4.36.0` ([direct download link](https://desktop.docker.com/win/main/amd64/175267/Docker%20Desktop%20Installer.exe?_gl=1*jsjynk*_ga*NDc3MTQ5NDkzLjE3MTAzMTQxMzA.*_ga_XJWPQMJYHQ*MTczMzM1NjcyNy4xMC4xLjE3MzMzNTczOTQuNjAuMC4w))
- Follow install instructions.

You may need to turn on virtualization support for your CPU (in BIOS).

Test in CLI to check install was successful:

    docker run hello-world

When docker prompt to share disk C, agree on that.

<img src="resources/share_docker_folder_windows.png" alt="">

Or, directly indicate directory on Settings after run `starcraft:game` once,

`Docker Desktop` > `Settings` > `Resources` > `File shareing` > `Virtual file shares`

Add `C:\Users\{user}\AppData\Roaming`

Enter yor credentials:

<img src="resources/share_docker_folder_permissions_windows.png" alt="">

Sometimes popup for entering your credentials could appear after VNC window, so don't miss it.

Now build the images required to run observer. Enter the docker directory and run `build_images.ps1`. Now you're setup to install observer to manage the game containers.

    cd docker
    build_images.sh

### Python & pip

Download and install Python 3.6 release from [Python releases for Windows](https://www.python.org/downloads/windows/)

You might need to [add python / pip to PATH](https://stackoverflow.com/a/4855685).

Install `observer` package in CLI:

    pip install .
    observer --install


### VNC
- [download RealVNC](https://www.realvnc.com/en/connect/download/viewer/windows/)

Install, and rename binary to `vnc-viewer.exe`, add the folder with the `vnc-viewer` binary to `PATH`.
