#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 

def get_domains():
	
	if len(sys.argv) < 2:
		print("Usage %s NUMBER" % sys.argv[0])
		sys.exit(1)
	number = int(sys.argv[1])
	domains = Domain.random(number)
	for domain in domains:
		print(domain)


get_domains()
sys.exit(0)