#!/usr/bin/env sh

# All shell variables listed here will be used to for application configuration
# Sections are broken down into function. Some are tightly coupled :(

# Override gunicorn launch options below. Negates Docker '-e' environmental run options
# export \
#  ACCESS_LOG="./access.log" \
#  CACERT="/certs/ca.pem" \
#  CERTFILE="/certs/cert.pem" \
#  CERTKEY="/certs/key.pem" \
#  CHECK_CERTS="1" \
#  CIPHERS="AES256+EECDH:AES256+EDH:!aNULL" \
#  IPV4="0.0.0.0" \
#  IPV6="[::]:1" \
#  PORT=80 \
#  WORKER_PROCS=4 \
#  GUNICORN_CMD='pymailadmin:create_app()'

# Application framework:
export \
  FLASK_DEBUG="False" \
  FLASK_DEBUG_WSGI="False" \
  FLASK_RUN_PORT=5080 \
  FLASK_INITIAL_ADMIN_ACCOUNT="pymailadmin" \
  FLASK_INITIAL_ADMIN_DOMAIN="mail.mailu.io" \
  FLASK_INITIAL_ADMIN_PW="pymailadmin" \
  FLASK_LOGLEVEL="info" \
  FLASK_RESOLVER_ATTEMPTS=20 \
  FLASK_RESOLVER_TIMEOUT_MIN=2 \
  FLASK_RESOLVER_TIMEOUT_MAX=5 

# Application configuration:
export \
  APP_BABEL_DEFAULT_LOCALE="en" \
  APP_BABEL_DEFAULT_TIMEZONE="UTC" \
  APP_BOOTSTRAP_SERVE_LOCAL="True" \
  APP_DOMAIN_REGISTRATION="False" \
  APP_PASSWORD_SCHEME="BLF-CRYPT" \
  APP_RECAPTCHA_PRIVATE_KEY="" \
  APP_RECAPTCHA_PUBLIC_KEY="" \
  APP_SITENAME="PyMailAdmin" \
  APP_TEMPLATES_AUTO_RELOAD="True" \
  APP_WEBSITE="https://mail.mailu.io" \
  APP_WEB_ADMIN="/admin" \
  APP_WEB_AUTH="/authentication" \
  APP_WEB_WEBMAIL="/webmail"

# Network :
# if cat /proc/sys/net/ipv6/bindipv6only -> 0
# just use ipv6 bind address, ipv4 will be inclusive
#export \
#  IP= \
#  IPV4= \
#  IPV6=

# Database (postgresql):
export \
  DB_HOST="mail_postgres_1" \
  DB_NAME="pymailadmin" \
  DB_PORT="5432" \
  DB_PW="pymailadmin" \
  DB_UPGRADE="False" \
  DB_USER="pymailadmin" \
  APP_DB_SQLALCHEMY_DATABASE_URI="postresql://${DB_USER}:${DB_PW}@${DB_HOST}:${DB_PORT}/${DB_NAME}" \
  APP_DB_SQLALCHEMY_TRACK_MODIFICATIONS="False"

# Hosts:
# !!!This is not a /etc/hosts file configuration!!!
# Set these to the container or servername if desired,
# to have docker resolve the hostname int/externally
export \
  HOST_ADMIN="mail_pymailadmin_1" \
  HOST_AV="mail_antivirus_1" \
  HOST_IMAP="mail_imap_1" \
  HOST_LMTP="mail_imap_1" \
  HOST_POP3="mail_imap_1" \
  HOST_POSTGRES="mail_postgres_1" \
  HOST_PROXY="mail_proxy_1" \
  HOST_REDIS="mail_redis_1" \
  HOST_SMTP="mail_smtp_1" \
  HOST_SPAM="mail_spam_1" \
  HOST_STATS="mail_stats_1" \
  HOST_WEBMAIL="mail_webmail_1" \
  HOST_WEBDAV="mail_webdav_1"

# Network hosts:
# !!!This is not a /etc/hosts file configuration!!!
# Set these to the container or servername if desired,
# to have docker resolve the hostname int/externally
#export \
#  NET_ADMIN="" \
#  NET_AV="" \
#  NET_IMAP="" \
#  NET_LMTP="" \
#  NET_POP3="" \
#  NET_POSTGRES="" \
#  NET_PROXY="" \
#  NET_REDIS="" \
#  NET_SMTP="" \
#  NET_SPAM="" \
#  NET_STATS="" \
#  NET_WEBMAIL="" \
#  NET_WEBDAV=""

# Ports:
export \
  PORT_IMAP_PLAIN=143 \
  PORT_IMAP_TLS=993 \
  PORT_POP3_PLAIN=110 \
  PORT_POP3_TLS=995 \
  PORT_SMTP_AUTH=465 \
  PORT_SMTP_PLAIN=25 \
  PORT_SMTP_TLS=587 \
  PORT_SPAM="" \
  PORT_STATS="" \
  PORT_WEBDAV="" \
  PORT_WEBMAIL_IMAP_PLAIN=10143 \
  PORT_WEBMAIL_IMAP_TLS=10993 \
  PORT_WEBMAIL_SMTP_PLAIN=10025 \
  PORT_WEBMAIL_SMTP_TLS=10587

# Mail:
export \
  MAIL_AUTH_RATELIMIT="10/minute;1000/hour" \
  MAIL_AUTH_RATELIMIT_SUBNET="True" \
  MAIL_DEFAULT_ALIASES=10 \
  MAIL_DEFAULT_QUOTA=1000000000 \
  MAIL_DEFAULT_USERS=10 \
  MAIL_DOMAIN="mailu.io" \
  MAIL_DMARC_RUA="None" \
  MAIL_DMARC_RUF="None" \
  MAIL_DKIM_SELECTOR="dkim" \
  MAIL_DKIM_PATH="/dkim/{domain}.{selector}.key" \
  MAIL_HOSTNAMES="mail.mailu.io,alternative.mailu.io" \
  MAIL_POSTMASTER="postmaster" \
  MAIL_QUOTA_STORAGE_URL="redis://{0}/1"
  MAIL_RATELIMIT_STORAGE_URL="redis://{0}/2" \
  MAIL_RECIPIENT_DELIMITER="+" \
  MAIL_SECRET_KEY="changeMe" \
  MAIL_SUBNET="192.168.0.0/24" \
  MAIL_SUBNET6="None" \
  MAIL_WELCOME="True" \
  MAIL_WELCOME_SUBJECT="Welcome to mail@${DOMAIN}" \
  MAIL_WELCOME_BODY="If you are reading this, your mail is configured!"

# Statistics:
export \
  STATS_ENABLE="False" \
  STATS_INSTANCE_ID_PATH="/data/instance" \
  STATS_ENDPOINT="0.{}.stats.${DOMAIN}"
