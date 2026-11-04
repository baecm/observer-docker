FROM starcraft:bwapi
LABEL maintainer="Michal Sustr <michal.sustr@aic.fel.cvut.cz>"

# xdotool drives the game window: auto launch, capture_movement and the
# Start click of a shared replay (play_common.sh)
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends xdotool \
    && rm -rf /var/lib/apt/lists/*

USER starcraft
WORKDIR $APP_DIR

COPY --chown=starcraft:users scripts/play_* ./
COPY --chown=starcraft:users scripts/hook_* ./

CMD ["/app/play_entrypoint.sh"]
