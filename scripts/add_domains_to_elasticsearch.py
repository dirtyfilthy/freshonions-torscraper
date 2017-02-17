#!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
from tor_elasticsearch import  *
import sys 

@db_session
def add_domains():
	domains = select(d for d in Domain)
	for domain in domains:
		dom = DomainDocType.from_obj(domain)
		dom.save()
		print(domain.host)


if is_elasticsearch_enabled():
	print("[+] Elastic search enabled")
else:
	print("[!] Elastic search disabled")
	sys.exit(1)

add_domains()
sys.exit(0)