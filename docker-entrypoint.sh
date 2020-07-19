#!/usr/bin/env sh
# vim:sw=4:ts=4:et
# taken from ngnix docker-entrypoint.sh
# modified 06/2020

set -e
if /usr/bin/find "/docker-entrypoint.d/" -mindepth 1 -maxdepth 1 -type f -print -quit 2>/dev/null | read v 
then
  echo "$0: /docker-entrypoint.d/ is not empty, will attempt to perform configuration"

  echo "$0: Looking for shell scripts in /docker-entrypoint.d/"
  if [ -f "/docker-entrypoint.d/S99-shell-config.sh" ]
  then
    echo "$0: S99-shell-config.sh found. Executing."
    . /docker-entrypoint.d/S99-shell-config.sh
  fi
  find "/docker-entrypoint.d/" -follow -type f -print | sort -n | while read -r f
  do
    case "$f" in
      *.sh)
        if [ -x "$f" ]
        then
          echo "$0: Launching $f";
          "$f"
        else
          # warn on shell scripts without exec bit
           echo "$0: Ignoring $f, not executable";
        fi
        ;;
      *.py)
        if [ -x "$f" ]
        then
          echo "$0: Launching $f";
          "$f"
        else
          # warn on shell scripts without exec bit
           echo "$0: Ignoring $f, not executable";
        fi
        ;;
      *) 
        echo "$0: Ignoring $f";
        ;;
    esac
  done
  echo "$0: Configuration complete; ready for start up"
else
  echo "$0: No files found in /docker-entrypoint.d/, skipping configuration"
fi
exec "$@"
