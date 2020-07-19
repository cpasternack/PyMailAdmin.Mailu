#!/usr/bin/env python3
import os
import logging as log
import sys

log.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"))

os.chdir("/app/")
stats = os.environ.get("STATS_ENABLE")

# if STATS_ENABLE is true
if stats:
  os.system("flask pymailadmin register_stats")
else:
  log.info("Stats endpoint not in use.")

sys.exit(0)
