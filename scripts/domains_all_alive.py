#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 

@db_session
def get_domains():
	domains = select(d for d in Domain if d.is_up == True)
	for domain in domains:
		print(domain.host)


get_domains()
sys.exit(0)