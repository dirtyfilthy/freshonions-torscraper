#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import os
import sys 

@db_session
def fix_subdomains():
	domains = select(d for d in Domain)
	for domain in domains:
		print(domain.host)
		if domain.host.count(".") > 1:
			domain.is_subdomain = True


fix_subdomains()
sys.exit(0)