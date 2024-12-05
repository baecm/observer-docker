#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Build images
docker build -f dockerfiles/wine.dockerfile -t starcraft:wine .
docker build -f dockerfiles/bwapi.dockerfile -t starcraft:bwapi .
docker build -f dockerfiles/play.dockerfile -t starcraft:play .
docker build -f dockerfiles/java.dockerfile -t starcraft:java .

# Change directory
pushd ../observer/local_docker

# Download the StarCraft zip if it doesn't exist
if [ ! -f "starcraft.zip" ]; then
    curl -o starcraft.zip http://files.theabyss.ru/sc/starcraft.zip
fi

# Build the final game image
docker build -f game.dockerfile -t "starcraft:game" .

# Return to the original directory
popd

# Script completed successfully
echo "All images built successfully!"