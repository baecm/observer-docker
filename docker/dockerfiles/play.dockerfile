FROM starcraft-cog:bwapi
LABEL maintainer="Cheong-mok Bae"

USER starcraft
WORKDIR $APP_DIR

COPY --chown=starcraft:users scripts/play_* ./
COPY --chown=starcraft:users scripts/hook_* ./

CMD ["/app/play_entrypoint.sh"]
