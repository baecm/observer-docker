FROM starcraft-cog:play
LABEL maintainer="Cheong-mok Bae"

ENV JAVA_DIR="$APP_DIR/java"

#####################################################################
USER starcraft
WORKDIR $APP_DIR

COPY --chown=starcraft:users jre-8u321-windows-i586.tar.gz jre.tar.gz
RUN set -x \
    && tar -xzf jre.tar.gz \
    && mv jre1.8.0_321/ $JAVA_DIR/ \
    && rm jre.tar.gz

COPY scripts/win_java32 /usr/bin/win_java32
