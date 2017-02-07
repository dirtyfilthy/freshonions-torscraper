#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import os
import sys 

def touch(fname, times=None):
    with open(fname, 'a+'):
        os.utime(fname, times)

def read_file_modification_time(fname):
	try:
		return datetime.datetime.fromtimestamp(os.path.getmtime(fname))
	except:
		return NEVER

@db_session
def get_domains_since_file_mod(fname):
	creation_horizon = read_file_modification_time(fname)
	touch(fname)
	domains = select(d for d in Domain if d.created_at > creation_horizon)
	for domain in domains:
		print(domain.host)


get_domains_since_file_mod(sys.argv[1])
sys.exit(0)