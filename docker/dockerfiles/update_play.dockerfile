FROM starcraft:game-1.0.4

ENV TM_DIR="$APP_DIR/tm"
WORKDIR /app

COPY --chown=starcraft:users ../tm $TM_DIR
