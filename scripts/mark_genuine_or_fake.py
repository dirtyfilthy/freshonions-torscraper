#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 

@db_session
def mark_genuine_or_fake(host, genuine):
	domain = Domain.find_by_url(host)
	if not domain:
		print("Domain %s not found!" % host)
		sys.exit(1)
	domain.manual_genuine = True
	if genuine:
		domain.is_genuine = True
		domain.is_fake = False
		print("Marked %s as genuine" % host)
	else:
		domain.is_genuine = False
		domain.is_fake = True
		print("Marked %s as fake" % host)
	commit()


if len(sys.argv) < 3 or not sys.argv[2].lower() in ["genuine", "fake"]:
	print("Usage: %s URL genuine|fake")


genuine = (sys.argv[2].lower() == "genuine")
host = sys.argv[1]
mark_genuine_or_fake(host, genuine)
sys.exit(0)