# do not publish starcraft:game

docker tag starcraft:wine  cjdahrl/starcraft:wine
docker tag starcraft:bwapi cjdahrl/starcraft:bwapi
docker tag starcraft:java  cjdahrl/starcraft:java
docker tag starcraft:play  cjdahrl/starcraft:play

docker push cjdahrl/starcraft:wine
docker push cjdahrl/starcraft:bwapi
docker push cjdahrl/starcraft:java
docker push cjdahrl/starcraft:play
