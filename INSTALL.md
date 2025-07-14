# Install

<!-- What works (has been tested): -->

  <!-- - _Linux_: headful/headless play, 1v1 (bot, human), VNC -->
  <!-- - Bot type: `AI_MODULE`, `EXE`, `JAVA_JNI`, `JAVA_MIRROR` -->
  <!-- - [Tested on all SSCAIT 2017 tournament bots (and works on most)](tested_bots.md) -->


Table of contents:

  * [Windows](#windows)
  * [Ubuntu](#ubuntu)
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

```bash
docker run hello-world
```

When docker prompt to share disk C, agree on that.

<img src="resources/share_docker_folder_windows.png" alt="">

Or, directly indicate directory on Settings after run `starcraft:game` once,

`Docker Desktop` > `Settings` > `Resources` > `File shareing` > `Virtual file shares`

Add `C:\Users\{user}\AppData\Roaming`

Enter yor credentials:

<img src="resources/share_docker_folder_permissions_windows.png" alt="">

Sometimes popup for entering your credentials could appear after VNC window, so don't miss it.

Now build the images required to run observer. Enter the docker directory and run `build_images.ps1`. Now you're setup to install observer to manage the game containers.

```bash
cd docker
build_images.ps1
```

When building the image for `starcraft:game`, there may be instances where Windows Defender quarantines the starcraft.zip file. To resolve this issue, simply allow the file through Windows Defender.

### Python & pip

Download and install Python 3.6 release from [Python releases for Windows](https://www.python.org/downloads/windows/)

You might need to [add python / pip to PATH](https://stackoverflow.com/a/4855685).

Install `observer` package in CLI:

```bash
pip install .
observer --install
```

### VNC
- [download RealVNC](https://www.realvnc.com/en/connect/download/viewer/windows/)

Install, and rename binary to `vnc-viewer.exe`, add the folder with the `vnc-viewer` binary to `PATH`.

## Ubuntu
### Docker
Based on https://docs.docker.com/engine/install/ubuntu/
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

Install the Docker packages

```bash
 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Test to check install was successful:

```bash
sudo docker run hello-world
```

Now build the images required to run sc-docker. Enter the docker directory and run ```build_images.sh```. Now you're setup to install scbw to manage the game containers.

```bash
cd docker
bash build_images.sh
```

### Python & pip
(use python3.6 instead of just python)

Lazy version with a lot of sudo (based on [this](https://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/))

```bash
pip install .
observer --install
```

### VNC
Install [RealVNC viewer](https://www.realvnc.com/) for viewing GUI headful modes from the docker images.

Save the executable in PATH so that it can be launched as vnc-viewer

```bash
sudo ln -s [where-you-put-vnc] /usr/bin/vnc-viewer
```

Quick links:
- [Download RealVNC](https://www.realvnc.com/en/connect/download/viewer/linux/)


