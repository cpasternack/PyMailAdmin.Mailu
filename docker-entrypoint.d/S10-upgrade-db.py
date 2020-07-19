#!/usr/bin/env python3

import os
import logging as log
import sys

log.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"))

os.chdir("/app/")
db_upgrade = os.environ.get("DB_UPGRADE")

# if upgrade db is not True or None (null/not set)
if db_upgrade or None:
  os.system("flask db upgrade")
  log.info("db -> upgraded")
else:
  log.info("database not upgraded")
sys.exit(0)
