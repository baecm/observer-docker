#!/bin/bash

docker image inspect observer:game > /dev/null
if [ $? -ne 0 ]; then
	docker run -v /var/run/docker.sock:/var/run/docker.sock -e STARCRAFT_UID=$(id -u) observer /bin/bash -c "cd observer/docker; ./build_images.sh"
	docker run -v /var/run/docker.sock:/var/run/docker.sock observer --install
fi

mkdir ~/.observer 2> /dev/null
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v ~/.observer:/root/.observer observer observer.play "$@"
