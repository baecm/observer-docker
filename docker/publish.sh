#!/usr/bin/env bash
set -eux

# do not publish starcraft:game
VERSION=$(python ../setup.py --version)

docker tag starcraft-cog:wine  cjdahrl/starcraft-cog:wine
docker tag starcraft-cog:bwapi cjdahrl/starcraft-cog:bwapi
docker tag starcraft-cog:java  cjdahrl/starcraft-cog:java
docker tag starcraft-cog:play  cjdahrl/starcraft-cog:play
docker tag starcraft-cog:game cjdahrl/starcraft-cog:game

docker tag starcraft-cog:wine  cjdahrl/starcraft-cog:wine-${VERSION}
docker tag starcraft-cog:bwapi cjdahrl/starcraft-cog:bwapi-${VERSION}
docker tag starcraft-cog:java  cjdahrl/starcraft-cog:java-${VERSION}
docker tag starcraft-cog:play  cjdahrl/starcraft-cog:play-${VERSION}
docker tag starcraft-cog:game cjdahrl/starcraft-cog:game-${VERSION}

docker push cjdahrl/starcraft-cog:wine
docker push cjdahrl/starcraft-cog:bwapi
docker push cjdahrl/starcraft-cog:java
docker push cjdahrl/starcraft-cog:play
docker push cjdahrl/starcraft-cog:wine-${VERSION}
docker push cjdahrl/starcraft-cog:bwapi-${VERSION}
docker push cjdahrl/starcraft-cog:java-${VERSION}
docker push cjdahrl/starcraft-cog:play-${VERSION}
