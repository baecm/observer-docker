#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Build images
docker build -f dockerfiles/wine.dockerfile -t starcraft:wine .
if [ $? -ne 0 ]; then
    echo "Failed to build starcraft:wine image"
    exit 1
fi

docker build -f dockerfiles/bwapi.dockerfile -t starcraft:bwapi .
if [ $? -ne 0 ]; then
    echo "Failed to build starcraft:bwapi image"
    exit 1
fi

docker build -f dockerfiles/play.dockerfile -t starcraft:play .
if [ $? -ne 0 ]; then
    echo "Failed to build starcraft:play image"
    exit 1
fi

docker build -f dockerfiles/java.dockerfile -t starcraft:java .
if [ $? -ne 0 ]; then
    echo "Failed to build starcraft:java image. You can verify that you will build with the proper version of Java in the file dockerfiles/play.dockerfile"
    exit 1
fi

# Change directory
pushd ../observer/local_docker

# Download the StarCraft zip if it doesn't exist
if [ ! -f "starcraft.zip" ]; then
    curl -o starcraft.zip http://files.theabyss.ru/sc/starcraft.zip
fi

# Build the final game image
docker build -f game.dockerfile -t "starcraft:game" .
if [ $? -ne 0 ]; then
    echo "Failed to build starcraft:game image"
    exit 1
fi

# Return to the original directory
popd

# Script completed successfully
echo "All images built successfully!"