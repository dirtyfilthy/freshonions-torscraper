 #!/usr/bin/python
from pony.orm import *
from datetime import *
from tor_db import *
import sys 
from tabulate import tabulate

@db_session
def ban(url):
	if not url:
		print("Usage: %s http://domain.onion/" % sys.argv[0])
		sys.exit(1)
	domain = Domain.find_by_url(url)
	if not domain:
		print("Could not find '%s'" % url)
		sys.exit(1)
	domain.is_banned = True
	domain.ban_exempt = False
	print("Banned '%s'" % url)

ban(sys.argv[1])
sys.exit(0)