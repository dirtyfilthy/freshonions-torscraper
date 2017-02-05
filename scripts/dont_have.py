#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys

@db_session
def print_lines():
	lines = [line.strip() for line in open(sys.argv[1])]
	for line in lines:
		try:
			d = Domain.get(host=line)
			if not d:
				print line
		except:
			continue

print_lines()
