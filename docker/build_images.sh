#!/usr/bin/env bash
set -eux

docker build -f dockerfiles/wine.dockerfile  -t starcraft-cog:wine   .
docker build -f dockerfiles/bwapi.dockerfile -t starcraft-cog:bwapi  .
docker build -f dockerfiles/play.dockerfile  -t starcraft-cog:play   .
docker build -f dockerfiles/java.dockerfile  -t starcraft-cog:java   .

pushd ../scbw/local_docker
[ ! -f starcraft.zip ] && curl -SL 'http://files.theabyss.ru/sc/starcraft.zip' -o starcraft.zip
docker build -f game.dockerfile  -t "starcraft-cog:game" .
popd
