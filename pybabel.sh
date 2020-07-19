#!/usr/bin/env sh

set -xe

if [ "$2" -eq "0" ]
then
  for locale in $1
  do
    pybabel compile -l ${locale} -d ${BABEL_TRANSLATE_APP}/translations
  done
elif [ "$2" -gt "0" ]
then
  for locale in $1
  do
    pybabel init -l ${locale} -i messages.pot -d ${BABEL_TRANSLATE_APP}/translations 
    pybabel compile -l ${locale} -d ${BABEL_TRANSLATE_APP}/translations
  done
else
  echo "$0: No translation provided or initialised" 
fi
exit $? 
