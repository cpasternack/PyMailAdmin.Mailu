# First stage to build assets
# bump to alpine latest (3.12) for TLSv1.3
ARG DISTRO=alpine:latest

# bump to 14.4. Node 10 LTS minimum for TLSv1.3
# build https://adminlte.io/ ADMINLTE boostrap template
# and jquery
# Build ADMINLTE and jquery assets
FROM node:14-alpine3.12 as assets

ADD package.json ./
RUN npm install -dd

ADD ./webpack.config.js ./
COPY ./assets ./assets
RUN mkdir static; \
  ./node_modules/.bin/webpack-cli

# Build PyMailAdmin application
FROM $DISTRO as application
RUN mkdir -p /app;
WORKDIR /app
ARG FLASK_BUILD_APP="pymailadmin"
ENV SYSTEM_USER=${FLASK_BUILD_APP}

# install python3/pip3, openssl
# create system user with no home or password
# cleanup build/install requirements for openssl, python3 utils, postgres
ADD requirements-prod.txt requirements.txt
RUN apk add --no-cache \
  python3 py3-pip git bash openssl curl postgresql-libs; \
  pip3 install --upgrade pip; \
  adduser -S -D -H ${SYSTEM_USER} -G users; \
  apk add --no-cache --virtual build-dep \
  openssl-dev libffi-dev python3-dev build-base postgresql-dev; \
  pip3 install -r requirements.txt; \
  apk del --no-cache build-dep

COPY --from=assets static ./${FLASK_BUILD_APP}/ui/static
ADD ${FLASK_BUILD_APP} ./${FLASK_BUILD_APP}
ADD migrations ./migrations
COPY ./license ./license

# init/compile translations
FROM application as translation
WORKDIR /app
ARG TRANSLATIONS="ca da de_DE en_GB es_ES fr_FR he hu is_IS it_IT ja_JP nb_NO nl pl pt ru sv zh_Hans_CN"
ARG TRANSLATE_INIT=0
ENV BABEL_TRANSLATE_APP=${FLASK_BUILD_APP}
ADD ./messages.pot ./messages.pot
ADD babel.cfg ./babel.cfg
# copy existing translatons separate build stage or local (ARG TRANSLATE_INIT=0)
# COPY --from=translate translations ./pymailadmin/translations
# COPY ./translations ./pymailadmin/translations
ADD ./pybabel.sh ./pybabel.sh
RUN chmod +x ./pybabel.sh; \
  ./pybabel.sh "${TRANSLATIONS}" ${TRANSLATE_INIT}; \
  rm messages.pot pybabel.sh

# Runtime Container
FROM translation
WORKDIR /
ADD docker-entrypoint.sh docker-entrypoint.sh
COPY ./docker-entrypoint.d docker-entrypoint.d
VOLUME ["/data","/dkim","/certs"]
RUN chown -R ${SYSTEM_USER}:users /app/ /docker-entrypoint.d/; \
  chown ${SYSTEM_USER}:users docker-entrypoint.sh; \
  chmod -R +x /docker-entrypoint.d/ docker-entrypoint.sh

USER ${SYSTEM_USER}
WORKDIR /app
ENV FLASK_APP=${FLASK_BUILD_APP} \
  ACCESS_LOG="./access.log" \
  CACERT="/certs/ca.pem" \
  CERTFILE="/certs/cert.pem" \
  CERTKEY="/certs/key.pem" \
  CHECK_CERTS="1" \
  CIPHERS="AES256+EECDH:AES256+EDH:!aNULL" \
  IPV4="0.0.0.0" \
  IPV6="[::]" \
  IP=${IPV4} \
  PORT=80 \
  WORKER_PROCS=4 \
  GUNICORN_CMD='pymailadmin:create_app()'

EXPOSE ${PORT}/tcp
ENTRYPOINT ["/docker-entrypoint.sh"]
# run as shell form because docker escape quoting is a mess
CMD gunicorn -w ${WORKER_PROCS} -b ${IP}:${PORT} --certfile ${CERTFILE} --keyfile ${CERTKEY} --ca-certs ${CACERT} --cert-reqs ${CHECK_CERTS} --ciphers ${CIPHERS} --access-logfile ${ACCESS_LOG} --preload  ${GUNICORN_CMD}
HEALTHCHECK CMD curl -f -L http://localhost/ui/login?next=ui.index || exit 1
