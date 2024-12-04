#!/usr/bin/env bash
set -eux

# do not publish observer:game
VERSION=$(python ../setup.py --version)

docker tag observer:wine  cjdahrl/observer:wine
docker tag observer:bwapi cjdahrl/observer:bwapi
docker tag observer:java  cjdahrl/observer:java
docker tag observer:play  cjdahrl/observer:play
docker tag observer:wine  cjdahrl/observer:wine-${VERSION}
docker tag observer:bwapi cjdahrl/observer:bwapi-${VERSION}
docker tag observer:java  cjdahrl/observer:java-${VERSION}
docker tag observer:play  cjdahrl/observer:play-${VERSION}

docker push cjdahrl/observer:wine
docker push cjdahrl/observer:bwapi
docker push cjdahrl/observer:java
docker push cjdahrl/observer:play
docker push cjdahrl/observer:wine-${VERSION}
docker push cjdahrl/observer:bwapi-${VERSION}
docker push cjdahrl/observer:java-${VERSION}
docker push cjdahrl/observer:play-${VERSION}
