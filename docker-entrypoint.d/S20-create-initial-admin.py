#!/usr/bin/env python3

import os
import logging as log
import sys

log.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"))

os.chdir("/app/")

account = os.environ.get("INITIAL_ADMIN_ACCOUNT")
domain = os.environ.get("INITIAL_ADMIN_DOMAIN")
password = os.environ.get("INITIAL_ADMIN_PW")

if not account and not domain and not password:
  """ 'ifmissing' : if user exists, nothing happens, else it will be created
      # manage.py:47 
  """
  mode = "ifmissing"
  log.info("Creating initial admin account %s@%s with mode %s",account,domain,mode)
  os.system("flask pymailadmin admin %s %s '%s' --mode %s" % (account, domain, password, mode))
else:
  log.info("Error reading INITIAL_ADMIN_ environment variables.")
  log.info("You must run \'flask pymailadmin admin <account> <domain> <password> --mode create\'")
sys.exit(0)
