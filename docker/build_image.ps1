# Exit immediately if a command fails
$ErrorActionPreference = "Stop"

# Build Docker images
docker build -f dockerfiles/wine.dockerfile  -t starcraft:wine   .
if (-not $?) {throw "Failed to build starcraft:wine image"}
docker build -f dockerfiles/bwapi.dockerfile -t starcraft:bwapi  .
if (-not $?) {throw "Failed to build starcraft:bwapi image"}
docker build -f dockerfiles/play.dockerfile  -t starcraft:play   .
if (-not $?) {throw "Failed to build starcraft:play image"}
docker build -f dockerfiles/java.dockerfile  -t starcraft:java   .
if (-not $?) {throw "Failed to build starcraft:java image. You can verify that you will build with proper version of Java in file dockerfiles/play.dockerfile"}


# Change directory
Push-Location ../observer/local_docker

# Download the StarCraft zip if it doesn't exist
if (!(Test-Path starcraft.zip))
{
    Invoke-WebRequest 'http://files.theabyss.ru/sc/starcraft.zip' -OutFile starcraft.zip
}

# Build the final game image
docker build -f game.dockerfile  -t "starcraft:game" .
if (-not $?) {throw "Failed to build starcraft:game image"}

# Return to the original directory
Pop-Location
