#!/usr/bin/env bash
set -eux

# do not publish starcraft:game
VERSION=$(python ../setup.py --version)

docker tag starcraft:wine  cjdahrl/starcraft:wine
docker tag starcraft:bwapi cjdahrl/starcraft:bwapi
docker tag starcraft:java  cjdahrl/starcraft:java
docker tag starcraft:play  cjdahrl/starcraft:play
docker tag starcraft:wine  cjdahrl/starcraft:wine-${VERSION}
docker tag starcraft:bwapi cjdahrl/starcraft:bwapi-${VERSION}
docker tag starcraft:java  cjdahrl/starcraft:java-${VERSION}
docker tag starcraft:play  cjdahrl/starcraft:play-${VERSION}

docker push cjdahrl/starcraft:wine
docker push cjdahrl/starcraft:bwapi
docker push cjdahrl/starcraft:java
docker push cjdahrl/starcraft:play
docker push cjdahrl/starcraft:wine-${VERSION}
docker push cjdahrl/starcraft:bwapi-${VERSION}
docker push cjdahrl/starcraft:java-${VERSION}
docker push cjdahrl/starcraft:play-${VERSION}
