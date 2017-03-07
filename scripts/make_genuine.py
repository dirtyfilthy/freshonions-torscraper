#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys

@db_session
def make_genuine():
	lines = [line.strip() for line in open(sys.argv[1])]
	for host in lines:
		domain = select(d for d in Domain if d.host==host).first()
		if not domain:
			print("Couldn't find %s" % host)
			continue
		if domain.is_genuine:
			continue
		print("Marking %s as genuine" % host)
		Domain.make_genuine(host)

make_genuine()
